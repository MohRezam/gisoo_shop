from django.contrib import admin

from apps.products.models import Bundle

import nested_admin


class BundleInline(nested_admin.NestedTabularInline):
    model = Bundle
    extra = 1

    fields = (
        "title",
        "quantity",
        "price",
        "is_active",
        "display_order",
    )
    exclude = ("creator",)


@admin.register(Bundle)
class BundleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "variant",
        "quantity",
        "price",
        "is_active",
        "display_order",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "title",
        "variant__sku",
        "variant__product__title",
    )

    ordering = (
        "display_order",
        "-created_at",
    )
    exclude = ("creator",)
