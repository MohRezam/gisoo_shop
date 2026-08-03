from django.contrib import admin

from apps.payments.models import Payment
from apps.shared.admin import BaseModelAdmin


@admin.register(Payment)
class PaymentAdmin(BaseModelAdmin):
    list_display = [
        "id",
        "order",
        "amount",
        "status",
        "gateway_payment_id",
        "gateway_reference_id",
        "paid_at",
        "created_at",
    ]

    list_filter = [
        "status",
        "created_at",
        "paid_at",
    ]

    search_fields = [
        "order__id",
        "order__phone_number",
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

    ordering = [
        "-created_at",
    ]

    list_select_related = [
        "order",
    ]
