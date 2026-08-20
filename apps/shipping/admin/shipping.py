from django.contrib import admin

from apps.shipping.models import (
    Shipment,
    ShippingMethod,
)


@admin.register(ShippingMethod)
class ShippingMethodAdmin(
    admin.ModelAdmin
):
    list_display = [
        "title",
        "price",
        "free_shipping_minimum",
        "estimated_days",
        "is_active",
    ]

    list_filter = [
        "is_active",
    ]

    search_fields = [
        "title",
    ]

    list_editable = [
        "price",
        "estimated_days",
        "is_active",
    ]

    ordering = [
        "price",
    ]
    exclude = ("creator",)



@admin.register(Shipment)
class ShipmentAdmin(
    admin.ModelAdmin
):
    list_display = [
        "id",
        "order",
        "status",
        "tracking_code",
        "shipped_at",
    ]

    list_filter = [
        "status",
    ]

    search_fields = [
        "tracking_code",
        "order__id",
    ]

    autocomplete_fields = [
        "order",
        "created_by",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
    ]

    ordering = [
        "-created_at",
    ]
    exclude = ("creator",)
