from django.contrib import admin

from apps.orders.models import (
    Order,
    OrderItem,
)


class OrderItemInline(admin.TabularInline):
    model = OrderItem

    extra = 0

    readonly_fields = [
        "variant",
        "product_title",
        "variant_sku",
        "quantity",
        "unit_price",
        "total_price",
    ]
    exclude = ("creator",)
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "status",
        "total_price",
        "phone_number",
        "created_at",
    ]

    list_filter = [
        "status",
        "created_at",
        "province",
        "city",
    ]

    search_fields = [
        "id",
        "user__phone_number",
        "receiver_name",
        "phone_number",
        "tracking_code"
    ]

    readonly_fields = [
        "total_price",
        "created_at",
        "updated_at",
        "expires_at",
    ]

    inlines = [
        OrderItemInline,
    ]

    ordering = [
        "-created_at",
    ]
    exclude = ("creator", "archived")
    raw_id_fields = ("user", "discount", "shipping_method")
    list_per_page = 15
    list_display_links = ("user",)
