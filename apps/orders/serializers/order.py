from rest_framework import serializers

from apps.orders.models import Order
from apps.payments.models import Payment


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


class OrderPaymentSerializer(
    serializers.ModelSerializer,
):
    class Meta:
        model = Payment

        fields = [
            "id",
            "amount",
            "status",
            "gateway_payment_id",
            "gateway_reference_id",
            "paid_at",
        ]


class OrderDetailSerializer(
    serializers.ModelSerializer,
):
    payment = OrderPaymentSerializer(
        read_only=True,
    )

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
            "payment",
            "created_at",
        ]