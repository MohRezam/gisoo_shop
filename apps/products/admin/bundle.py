from django.contrib import admin

from apps.products.models import Bundle


class BundleInline(admin.TabularInline):
    model = Bundle
    extra = 1

    fields = (
        "title",
        "price",
        "is_active",
        "display_order",
    )


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