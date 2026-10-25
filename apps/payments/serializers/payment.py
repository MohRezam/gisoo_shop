from rest_framework import serializers

from apps.payments.models import PaymentIntent, PaymentReceipt, PaymentIntentStatus
from apps.payments.services.checkout_settings import (
    payment_support_url,
    payment_terms_lines,
)
from apps.payments.services.sheba import visible_sheba
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
    expires_at = serializers.SerializerMethodField()
    payable_amount = serializers.SerializerMethodField()
    amount_unit = serializers.SerializerMethodField()
    terms = serializers.SerializerMethodField()
    support_url = serializers.SerializerMethodField()

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
            "payable_amount",
            "amount_unit",
            "destination_card",
            "terms",
            "support_url",
            "status",
            "expires_at",
            "server_time",
            "submitted_at",
            "reviewed_at",
            "paid_at",
            "rejection_reason",
        ]
        read_only_fields = fields

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
        card = obj.destination_card
        return {
            "masked_pan": card.masked_pan,
            "display_pan": card.display_pan,
            "name": card.name,
            "bank_name": card.bank_name or "",
            "sheba": visible_sheba(
                card=card,
                order_total_toman=obj.order.total_price or 0,
            ),
        }

    def get_terms(self, obj):
        return payment_terms_lines()

    def get_support_url(self, obj):
        return payment_support_url()

    def get_payable_amount(self, obj):
        """Exact card-to-card amount in RIAL (same as payable_amount_rial)."""
        return obj.payable_amount_rial

    def get_amount_unit(self, obj):
        return {
            "code": "rial",
            "label": "ریال",
        }

    def get_server_time(self, obj):
        return timezone.now()

    def get_expires_at(self, obj):
        """
        expires_at is only meaningful while the customer
        has an active payment deadline.

        Once a receipt has been submitted, the customer
        is waiting for admin review, so the frontend must
        not show a countdown.
        """

        if obj.status in {
            PaymentIntentStatus.PENDING_PAYMENT,
            PaymentIntentStatus.REJECTED,
        }:
            return obj.expires_at

        return None
