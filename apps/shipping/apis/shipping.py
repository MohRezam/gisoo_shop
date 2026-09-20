from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from apps.shipping.cache import (
    get_cached_shipping_methods,
    set_cached_shipping_methods,
)
from apps.shipping.models import ShippingMethod
from apps.shipping.serializers import ShippingMethodSerializer


@extend_schema(
    tags=["Shipping"],
    summary="List shipping methods",
    description=(
        "Active shipping methods. `price` and `free_shipping_minimum` are in تومان. "
        "When cart products total >= `free_shipping_minimum`, shipping fee is 0. "
        "Response is cached briefly."
    ),
    responses={
        200: OpenApiResponse(
            response=ShippingMethodSerializer(many=True),
            examples=[
                OpenApiExample(
                    "Methods",
                    value=[
                        {
                            "id": 1,
                            "title": "پست پیشتاز",
                            "price": 50000,
                            "free_shipping_minimum": 1500000,
                            "estimated_days": 3,
                        }
                    ],
                )
            ],
        )
    },
)
class ShippingMethodListAPIView(ListAPIView):
    serializer_class = ShippingMethodSerializer

    queryset = (
        ShippingMethod.objects.filter(is_active=True).order_by("price")
    )

    def list(self, request, *args, **kwargs):
        cached = get_cached_shipping_methods()
        if cached is not None:
            return Response(cached)

        response = super().list(request, *args, **kwargs)
        # Paginated or plain list — cache the serialized payload
        set_cached_shipping_methods(response.data)
        return response
