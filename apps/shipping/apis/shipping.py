from rest_framework.generics import (
    ListAPIView,
)

from apps.shipping.models import (
    ShippingMethod,
)
from apps.shipping.serializers import (
    ShippingMethodSerializer,
)


class ShippingMethodListAPIView(
    ListAPIView
):
    serializer_class = (
        ShippingMethodSerializer
    )

    queryset = (
        ShippingMethod.objects
        .filter(
            is_active=True,
        )
        .order_by("price")
    )
