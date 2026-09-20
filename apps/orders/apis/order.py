from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Order, OrderStatus, OrderItem
from apps.orders.serializers import (
    CreateOrderSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
    TrackOrderQuerySerializer,
)
from apps.orders.services.create_order import create_order
from apps.orders.services.track_order import build_track_payload
from apps.orders.cache import (
    get_cached_track_payload,
    set_cached_track_payload,
)
from utils.paginators import StandardResultPagination

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from django.db.models import Prefetch
from utils.paginators import StandardResultPagination

CUSTOMER_ORDER_STATUSES = [
    OrderStatus.CREATED,
    OrderStatus.PAYMENT_REJECTED,
    OrderStatus.PREPARING,
    OrderStatus.SHIPPED,
    OrderStatus.DELIVERED,
    OrderStatus.CANCELED,
    OrderStatus.EXPIRED
]


def get_customer_orders_queryset(user):
    return (
        Order.objects
        .filter(
            user=user,
            status__in=CUSTOMER_ORDER_STATUSES,
        )
        .select_related(
            "shipping_method",
        )
        .prefetch_related(
            Prefetch(
                "items",
                queryset=(
                    OrderItem.objects
                    .select_related(
                        "variant__product",
                    )
                    .prefetch_related(
                        "variant__product__images",
                    )
                ),
            ),
            "bundles",
            "payment_intents",
        )
        .order_by("-created_at")
    )


CREATE_ORDER_RESPONSE_EXAMPLE = {
    "id": 15,
    "public_number": "GS-260920-00015",
    "status": "waiting_payment",
    "products_price": 800000,
    "shipping_price": 50000,
    "discount_amount": 0,
    "total_price": 850000,
    "expires_at": "2026-09-20T22:45:00+03:30",
    "phone_number": "09120000000",
    "province": "تهران",
    "city": "تهران",
    "postal_code": "1234567890",
    "address": "خیابان مثال",
    "description": "Leave at the door",
    "tracking_code": "",
    "shipping_method_title": "پست پیشتاز",
    "payment": {
        "id": 9,
        "amount": 850000,
        "status": "pending",
        "gateway_payment_id": "",
        "gateway_reference_id": "",
        "paid_at": None,
    },
    "payment_intent": {
        "id": 12,
        "token": "xY9kLmN2pQ...",
        "status": "pending_payment",
        "payable_amount": 850000,
        "amount_unit": {"code": "toman", "label": "تومان"},
        "destination_card": "6037990000000000",
        "bank_name": "بانک ملی",
        "holder_name": "گیسو سنتر",
        "expires_at": "2026-09-21T22:00:00+03:30",
        "order_id": 15,
        "can_upload_receipt": True,
        "public_number": "GS-260920-00015",
        "rejection_reason": "",
        "receipt_uploaded_at": None,
        "created_at": "2026-09-20T22:00:00+03:30",
    },
    "created_at": "2026-09-20T22:00:00+03:30",
}


@extend_schema(
    tags=["Orders"],
    summary="Create Order",
    description=(
        "Creates a new order from the authenticated user's active cart.\n\n"
        "Sets status to `waiting_payment`, assigns `public_number`, creates a "
        "C2C `payment_intent`, and returns full pricing + shipping snapshot.\n\n"
        "Amounts are in تومان."
    ),
    request=CreateOrderSerializer,
    responses={
        201: OpenApiResponse(
            response=OrderDetailSerializer,
            description="Order created successfully.",
            examples=[
                OpenApiExample("Created", value=CREATE_ORDER_RESPONSE_EXAMPLE),
            ],
        ),
        400: OpenApiResponse(
            description="Invalid request, empty cart or invalid address.",
        ),
        401: OpenApiResponse(
            description="Authentication required.",
        ),
    },
)
class CreateOrderAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = create_order(
            user=request.user,
            address_id=serializer.validated_data["address_id"],
            shipping_method_id=serializer.validated_data["shipping_method_id"],
            description=serializer.validated_data.get("description", ""),
        )

        return Response(
            OrderDetailSerializer(order, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    tags=["Orders"],
    summary="My orders",
    description="Paginated list of the authenticated user's orders (newest first).",
    responses={200: OrderListSerializer(many=True)},
)
class MyOrdersListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderListSerializer
    pagination_class = StandardResultPagination

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .prefetch_related("payment_intents__destination_card")
            .order_by("-created_at")
        )


@extend_schema(
    tags=["Orders"],
    summary="My latest order",
    responses={
        200: OrderDetailSerializer,
        404: OpenApiResponse(description="No orders yet."),
    },
)
class MyLatestOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        order = (
            Order.objects.filter(user=request.user)
            .select_related("shipping_method", "payment")
            .prefetch_related("payment_intents__destination_card")
            .order_by("-created_at")
            .first()
        )
        if order is None:
            return Response(
                {"detail": "No orders found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            OrderDetailSerializer(order, context={"request": request}).data
        )


@extend_schema(
    tags=["Orders"],
    summary="Track order",
    description=(
        "Track an order by `public_number` + phone (login optional). "
        "Works for guests and authenticated users."
    ),
    parameters=[
        OpenApiParameter(name="code", required=True, type=str, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="phone", required=True, type=str, location=OpenApiParameter.QUERY),
    ],
    responses={
        200: OpenApiResponse(
            examples=[
                OpenApiExample(
                    "Track",
                    value={
                        "public_number": "GS-260920-00015",
                        "status": "preparing",
                        "status_label": "در حال آماده‌سازی",
                        "tracking_code": "1234567890",
                        "steps": [
                            {
                                "key": "created",
                                "label": "ثبت سفارش",
                                "done": True,
                                "at": "2026-09-20T22:00:00+03:30",
                            }
                        ],
                        "items_summary": "شامپو ضد ریزش",
                    },
                )
            ]
        ),
        404: OpenApiResponse(description="Order not found."),
    },
)
class TrackOrderAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        query = TrackOrderQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)

        order = (
            Order.objects.filter(
                public_number=query.validated_data["code"],
                phone_number=query.validated_data["phone"],
            )
            .prefetch_related("items", "shipments", "payment_intents")
            .first()
        )
        if order is None:
            return Response(
                {"detail": "Order not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        code = query.validated_data["code"]
        phone = query.validated_data["phone"]
        cached = get_cached_track_payload(code, phone)
        if cached is not None:
            return Response(cached)

        payload = build_track_payload(order)
        set_cached_track_payload(code, phone, payload)
        return Response(payload)


@extend_schema(
    tags=["Orders"],
    summary="Retrieve Order",
    description="Returns details of one of the authenticated user's orders.",
    responses={
        200: OrderDetailSerializer,
        401: OpenApiResponse(description="Authentication required."),
        404: OpenApiResponse(description="Order not found."),
    },
)
class OrderDetailAPIView(RetrieveAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return (
            Order.objects.select_related("payment", "shipping_method")
            .prefetch_related("payment_intents__destination_card")
            .filter(user=self.request.user)
        )
