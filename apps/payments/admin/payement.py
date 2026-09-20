from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.payments.models import (
    Payment,
    PaymentDestinationCard,
    PaymentIntent,
)
from apps.payments.services.review_payment_intent import (
    approve_payment_intent,
    reject_payment_intent,
)
from apps.shared.admin import BaseModelAdmin


@admin.register(DestinationCard)
class DestinationCardAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "masked_pan",
        "is_active",
        "created_at",
    ]
    list_filter = ["status", "created_at", "paid_at"]
    search_fields = [
        "order__id",
        "order__phone_number",
        "order__public_number",
        "gateway_payment_id",
        "gateway_reference_id",
    ]
    readonly_fields = [
        "order",
        "amount",
        "status",
        "gateway_payment_id",
        "gateway_reference_id",
        "paid_at",
        "created_at",
        "updated_at",
    ]
    ordering = ["-created_at"]
    list_select_related = ["order"]


@admin.register(PaymentDestinationCard)
class PaymentDestinationCardAdmin(BaseModelAdmin):
    list_display = ["id", "holder_name", "bank_name", "card_number", "is_active"]
    list_filter = ["is_active", "bank_name"]
    search_fields = ["card_number", "holder_name", "bank_name"]


@admin.register(PaymentIntent)
class PaymentIntentAdmin(BaseModelAdmin):
    list_display = [
        "id",
        "order",
        "status",
        "payable_amount",
        "destination_card",
        "expires_at",
        "created_at",
    ]
    list_filter = ["status", "created_at"]
    search_fields = ["token", "order__public_number", "order__phone_number"]
    readonly_fields = ["token", "created_at", "updated_at", "receipt_uploaded_at"]
    actions = ["approve_selected", "reject_selected"]
    list_select_related = ["order", "destination_card"]

    @admin.action(description=_("Approve selected payment intents"))
    def approve_selected(self, request, queryset):
        for intent in queryset:
            try:
                approve_payment_intent(intent=intent, reviewed_by=request.user)
            except Exception:
                continue

    @admin.action(description=_("Reject selected payment intents"))
    def reject_selected(self, request, queryset):
        for intent in queryset:
            try:
                reject_payment_intent(
                    intent=intent,
                    reviewed_by=request.user,
                    reason="Rejected by admin.",
                )
            except Exception:
                continue
