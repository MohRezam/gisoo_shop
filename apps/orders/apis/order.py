from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Order
from apps.orders.serializers import (
    CreateOrderSerializer,
    OrderDetailSerializer,
)
from apps.orders.services.create_order import (
    create_order,
)

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
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
    summary="Retrieve Order",
    description="Returns details of one of the authenticated user's orders.",
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
    serializer_class = (
        OrderDetailSerializer
    )

    permission_classes = [
        IsAuthenticated,
    ]

    lookup_field = "id"

    def get_queryset(
            self,
    ):
        return (
            Order.objects
            .select_related(
                "payment",
            )
            .filter(
                user=self.request.user,
            )
        )
