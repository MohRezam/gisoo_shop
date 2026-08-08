from django.contrib import admin

from apps.products.models import Banner


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "link_type",
        "display_order",
        "is_active",
        "created_at",
    )

    list_filter = (
        "link_type",
        "is_active",
    )

    search_fields = (
        "title",
    )

    list_editable = (
        "display_order",
        "is_active",
    )

    autocomplete_fields = (
        "product",
        "category",
    )

    ordering = (
        "display_order",
        "-created_at",
    )
