from django.contrib import admin

from apps.products.models import Bundle, BundleItem
from apps.shared.admin import BaseModelAdmin


class BundleInline(admin.TabularInline):
    model = Bundle
    extra = 1

    fields = (
        "title",
        "price",
        "is_active",
        "display_order",
    )


class BundleItemInline(admin.TabularInline):
    model = BundleItem
    extra = 1

    autocomplete_fields = (
        "variant",
    )


@admin.register(Bundle)
class BundleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "product",
        "price",
        "is_active",
        "display_order",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "title",
        "product__title",
    )

    list_select_related = (
        "product",
    )

    autocomplete_fields = (
        "product",
    )

    inlines = [
        BundleItemInline,
    ]


@admin.register(BundleItem)
class BundleItemAdmin(admin.ModelAdmin):
    list_display = (
        "bundle",
        "variant",
        "quantity",
    )

    search_fields = (
        "bundle__title",
        "variant__sku",
        "variant__product__title",
    )

    list_select_related = (
        "bundle",
        "variant",
        "variant__product",
    )

    autocomplete_fields = (
        "bundle",
        "variant",
    )