from django.db.models import Prefetch
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Order, OrderItem, OrderStatus
from apps.orders.ordering import apply_status_priority_ordering
from apps.orders.serializers import (
    CreateOrderSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
)
from apps.orders.services.create_order import create_order
from apps.orders.services.change_order_status import change_order_status
from apps.orders.services.delivery_confirm import (
    customer_can_confirm_delivery,
)
from apps.payments.models import PaymentIntentStatus
from utils.paginators import StandardResultPagination

CUSTOMER_ORDER_STATUSES = [
    OrderStatus.WAITING_PAYMENT,
    OrderStatus.PAYMENT_REJECTED,
    OrderStatus.PREPARING,
    OrderStatus.SHIPPED,
    OrderStatus.DELIVERED,
    OrderStatus.CANCELED,
    OrderStatus.EXPIRED,
]

VALID_STATUS_FILTERS = {choice.value for choice in OrderStatus}


CUSTOMER_CANCELABLE_STATUSES = {
    OrderStatus.WAITING_PAYMENT,
    OrderStatus.PAYMENT_REJECTED,
}


def customer_can_cancel_order(order) -> bool:
    """
    Customer may cancel only before uploading a payment receipt.
    Once a receipt is submitted (under review), cancel is blocked
    even while the order status is still waiting_payment.
    Expired / past-deadline unpaid orders are also not cancelable.
    """
    if order.status not in CUSTOMER_CANCELABLE_STATUSES:
        return False

    from django.utils import timezone

    now = timezone.now()
    if order.expires_at is not None and order.expires_at <= now:
        return False

    return not order.payment_intents.filter(
        status=PaymentIntentStatus.RECEIPT_SUBMITTED,
    ).exists()


def get_customer_orders_queryset(user, *, statuses=None):
    queryset = (
        Order.objects.filter(
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
                    OrderItem.objects.select_related(
                        "variant__product",
                    ).prefetch_related(
                        "variant__product__images",
                    )
                ),
            ),
            "bundles",
            "payment_intents",
        )
    )

    if statuses:
        queryset = queryset.filter(status__in=statuses)

    return apply_status_priority_ordering(queryset)


def parse_status_filter(raw_value) -> list[str] | None:
    if raw_value is None:
        return None
    parts = [
        part.strip().lower()
        for part in str(raw_value).split(",")
        if part and part.strip()
    ]
    if not parts:
        return None
    return [part for part in parts if part in VALID_STATUS_FILTERS]


@extend_schema(
    tags=["Orders"],
    summary="Create Order",
    description=(
            "Creates a new order from the authenticated user's "
            "active shopping cart."
    ),
    request=CreateOrderSerializer,
    responses={
        201: OpenApiResponse(
            response=OrderDetailSerializer,
            description="Order created successfully.",
        ),
        400: OpenApiResponse(
            description="Invalid request, empty cart or invalid address.",
        ),
        401: OpenApiResponse(
            description="Authentication required.",
        ),
    },
    examples=[
        OpenApiExample(
            "Request",
            request_only=True,
            value={
                "address_id": 1,
                "shipping_method_id": 2,
                "description": "Leave at the door",
            },
        ),
        OpenApiExample(
            "Success Response",
            response_only=True,
            value={
                "id": 15,
                "status": "waiting_payment",
                "total_price": 850000,
            },
        ),
    ],
)
class CreateOrderAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        serializer = CreateOrderSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        order = create_order(
            user=request.user,
            address_id=serializer.validated_data[
                "address_id"
            ],
            shipping_method_id=serializer.validated_data[
                "shipping_method_id"
            ],
            description=serializer.validated_data.get(
                "description",
                "",
            ),
        )

        return Response(
            OrderDetailSerializer(
                order,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    tags=["Orders"],
    summary="Retrieve My Order",
    description=(
            "Returns details of one of the authenticated user's "
            "orders that is currently being prepared or has been shipped."
    ),
    responses={
        200: OrderDetailSerializer,
        401: OpenApiResponse(
            description="Authentication required.",
        ),
        404: OpenApiResponse(
            description="Order not found.",
        ),
    },
)
class OrderDetailAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, id):
        order = (
            get_customer_orders_queryset(
                request.user,
            )
            .filter(
                id=id,
            )
            .first()
        )

        if order is None:
            return Response(
                {
                    "detail": "Order not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            OrderDetailSerializer(
                order,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["Orders"],
    summary="Cancel My Order",
    description=(
        "Cancels one of the authenticated user's unpaid orders "
        "(waiting_payment or payment_rejected) only before a "
        "payment receipt has been submitted. Orders with a "
        "receipt under review cannot be canceled."
    ),
    responses={
        200: OrderDetailSerializer,
        400: OpenApiResponse(
            description="Order cannot be canceled in its current status.",
        ),
        401: OpenApiResponse(
            description="Authentication required.",
        ),
        404: OpenApiResponse(
            description="Order not found.",
        ),
    },
)
class CancelOrderAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, id):
        order = (
            get_customer_orders_queryset(
                request.user,
            )
            .filter(
                id=id,
            )
            .first()
        )

        if order is None:
            return Response(
                {
                    "detail": "Order not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not customer_can_cancel_order(order):
            return Response(
                {
                    "detail": "این سفارش قابل لغو نیست.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        order = change_order_status(
            order=order,
            new_status=OrderStatus.CANCELED,
            changed_by=request.user,
            reason="canceled_by_customer",
        )

        return Response(
            OrderDetailSerializer(
                order,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["Orders"],
    summary="Confirm Delivery",
    description=(
        "Marks a shipped order as delivered after the customer "
        "confirms receipt. Available from the shipping min estimate "
        "until the auto-deliver deadline."
    ),
    responses={
        200: OrderDetailSerializer,
        400: OpenApiResponse(
            description="Order cannot be confirmed in its current state.",
        ),
        401: OpenApiResponse(
            description="Authentication required.",
        ),
        404: OpenApiResponse(
            description="Order not found.",
        ),
    },
)
class ConfirmDeliveryAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, id):
        order = (
            get_customer_orders_queryset(
                request.user,
            )
            .filter(
                id=id,
            )
            .first()
        )

        if order is None:
            return Response(
                {
                    "detail": "Order not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not customer_can_confirm_delivery(order):
            return Response(
                {
                    "detail": "تأیید تحویل برای این سفارش در دسترس نیست.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        order = change_order_status(
            order=order,
            new_status=OrderStatus.DELIVERED,
            changed_by=request.user,
            reason="confirmed_by_customer",
        )

        return Response(
            OrderDetailSerializer(
                order,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["Orders"],
    summary="List My Orders",
    description=(
        "Returns the authenticated user's orders, ordered with "
        "«در حال آماده‌سازی» first, then other statuses by priority. "
        "Supports status filter and page pagination."
    ),
    parameters=[
        OpenApiParameter(
            name="status",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
            description=(
                "Filter by status. Comma-separated values allowed, e.g. "
                "preparing,shipped"
            ),
        ),
        OpenApiParameter(
            name="page",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
        ),
        OpenApiParameter(
            name="page_size",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
        ),
    ],
    responses={
        200: OrderListSerializer(many=True),
        401: OpenApiResponse(
            description="Authentication required.",
        ),
    },
)
class OrderListAPIView(ListAPIView):
    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = OrderListSerializer
    pagination_class = StandardResultPagination

    def get_queryset(self):
        statuses = parse_status_filter(self.request.query_params.get("status"))
        return get_customer_orders_queryset(
            self.request.user,
            statuses=statuses,
        )


@extend_schema(
    tags=["Orders"],
    summary="Get Latest My Order",
    description=(
            "Returns the authenticated user's latest order "
            "that is currently being prepared or has been shipped."
    ),
    responses={
        200: OrderDetailSerializer,
        401: OpenApiResponse(
            description="Authentication required.",
        ),
        404: OpenApiResponse(
            description="No active order found.",
        ),
    },
)
class LatestOrderAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):
        order = (
            get_customer_orders_queryset(
                request.user,
            )
            .first()
        )

        if order is None:
            return Response(
                None,
                status=status.HTTP_200_OK,
            )

        return Response(
            OrderDetailSerializer(
                order,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )
