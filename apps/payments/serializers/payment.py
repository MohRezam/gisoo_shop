from rest_framework import serializers

from apps.payments.models import PaymentIntent, PaymentReceipt
from django.utils import timezone


class PaymentReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentReceipt
        fields = [
            "id",
            "original_name",
            "mime_type",
            "file_size",
            "sha256",
            "is_active",
            "uploaded_at",
        ]
        read_only_fields = fields


class PaymentIntentSerializer(serializers.ModelSerializer):
    order = serializers.SerializerMethodField()
    destination_card = serializers.SerializerMethodField()
    server_time = serializers.SerializerMethodField()

    class Meta:
        model = PaymentIntent
        fields = [
            "id",
            "token",
            "order",
            "base_amount_rial",
            "unique_suffix",
            "adjustment_discount",
            "payable_amount_rial",
            "destination_card",
            "status",
            "expires_at",
            "server_time",
            "submitted_at",
            "reviewed_at",
            "paid_at",
        ]
        read_only_fields = fields

    def get_server_time(self, obj):
        return timezone.now()

    def get_order(self, obj):
        return {
            "id": obj.order.id,
            "public_number": getattr(
                obj.order,
                "public_number",
                str(obj.order.id),
            ),
        }

    def get_destination_card(self, obj):
        return {
            "masked_pan": obj.destination_card.masked_pan,
            "display_pan": obj.destination_card.display_pan,
            "name": obj.destination_card.name,
        }
