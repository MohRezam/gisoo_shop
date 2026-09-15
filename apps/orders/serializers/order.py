from rest_framework import serializers

from apps.orders.models import Order


class CreateOrderSerializer(
    serializers.Serializer,
):
    address_id = serializers.IntegerField()

    shipping_method_id = (
        serializers.IntegerField()
    )

    description = serializers.CharField(
        required=False,
        allow_blank=True,
    )


class OrderDetailSerializer(
    serializers.ModelSerializer,
):
    class Meta:
        model = Order

        fields = [
            "id",
            "status",
            "products_price",
            "shipping_price",
            "discount_amount",
            "total_price",
            "expires_at",
            "phone_number",
            "province",
            "city",
            "postal_code",
            "address",
            "description",
            "created_at",
        ]