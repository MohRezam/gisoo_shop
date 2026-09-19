from rest_framework import status
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Order, OrderStatus, OrderItem
from apps.orders.serializers import (
    CreateOrderSerializer,
    OrderDetailSerializer, OrderListSerializer,
)
from apps.orders.services.create_order import (
    create_order,
)

from drf_spectacular.utils import (
    OpenApiExample,
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
    summary="List My Active Orders",
    description=(
            "Returns the authenticated user's orders that are "
            "currently being prepared or have been shipped."
    ),
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
        return get_customer_orders_queryset(
            self.request.user,
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

