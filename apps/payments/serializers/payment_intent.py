from rest_framework import serializers

from apps.payments.constants import PAYMENT_AMOUNT_UNIT, PAYMENT_AMOUNT_UNIT_LABEL
from apps.payments.models import PaymentIntent


class PaymentIntentSerializer(serializers.ModelSerializer):
    """
    Card-to-card payment intent payload for the shop frontend.

    `payable_amount` is always in تومان (toman / IRT).
    """

    destination_card = serializers.CharField(source="destination_card.card_number")
    bank_name = serializers.CharField(source="destination_card.bank_name")
    holder_name = serializers.CharField(source="destination_card.holder_name")
    order_id = serializers.IntegerField(read_only=True)
    can_upload_receipt = serializers.BooleanField(read_only=True)
    public_number = serializers.SerializerMethodField()
    amount_unit = serializers.SerializerMethodField()

    class Meta:
        model = PaymentIntent
        fields = [
            "id",
            "token",
            "status",
            "payable_amount",
            "amount_unit",
            "destination_card",
            "bank_name",
            "holder_name",
            "expires_at",
            "order_id",
            "can_upload_receipt",
            "public_number",
            "rejection_reason",
            "receipt_uploaded_at",
            "created_at",
        ]
        read_only_fields = fields

    def get_public_number(self, obj):
        return getattr(obj.order, "public_number", None) or None

    def get_amount_unit(self, obj):
        return {
            "code": PAYMENT_AMOUNT_UNIT,
            "label": PAYMENT_AMOUNT_UNIT_LABEL,
        }


class UploadReceiptSerializer(serializers.Serializer):
    receipt = serializers.ImageField()
