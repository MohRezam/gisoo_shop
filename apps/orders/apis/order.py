from rest_framework import status
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Order, OrderStatus
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

from utils.paginators import StandardResultPagination


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

    def post(
            self,
            request,
    ):
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
            {
                "id": order.id,
                "status": order.status,
                "total_price": order.total_price,
            },
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
class OrderDetailAPIView(
    RetrieveAPIView,
):
    serializer_class = OrderDetailSerializer

    permission_classes = [
        IsAuthenticated,
    ]

    lookup_field = "id"

    def get_queryset(
            self,
    ):
        return (
            Order.objects
            .filter(
                user=self.request.user,
                status__in=[
                    OrderStatus.PREPARING,
                    OrderStatus.SHIPPED,
                ],
            )
            .prefetch_related(
                "items",
            )
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
class OrderListAPIView(
    ListAPIView,
):
    serializer_class = OrderListSerializer

    permission_classes = [
        IsAuthenticated,
    ]
    pagination_class = StandardResultPagination

    def get_queryset(
            self,
    ):
        return (
            Order.objects
            .filter(
                user=self.request.user,
                status__in=[
                    "preparing",
                    "shipped",
                ],
            )
            .prefetch_related(
                "items",
            )
            .order_by(
                "-created_at",
            )
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
class LatestOrderAPIView(
    APIView,
):
    permission_classes = [
        IsAuthenticated,
    ]

    def get(
            self,
            request,
    ):
        order = (
            Order.objects
            .filter(
                user=request.user,
                status__in=[
                    "preparing",
                    "shipped",
                ],
            )
            .prefetch_related(
                "items",
            )
            .order_by(
                "-created_at",
            )
            .first()
        )

        if order is None:
            return Response(
                {
                    "detail": "No active order found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            OrderDetailSerializer(order).data,
        )
