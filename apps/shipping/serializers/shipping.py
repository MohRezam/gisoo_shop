from rest_framework import serializers

from apps.shipping.models import (
    ShippingMethod,
)


class ShippingMethodSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = ShippingMethod

        fields = [
            "id",
            "title",
            "price",
            "free_shipping_minimum",
            "estimated_days",
        ]