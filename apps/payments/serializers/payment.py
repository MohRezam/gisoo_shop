from rest_framework import serializers

from apps.payments.models import Payment


class PaymentSerializer(
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
            "created_at",
        ]

        read_only_fields = fields


class StartPaymentSerializer(
    serializers.Serializer,
):
    payment_id = serializers.IntegerField()