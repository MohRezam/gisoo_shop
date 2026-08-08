from django.contrib import admin

from apps.home.models import Banner
from apps.shared.admin import BaseModelAdmin


@admin.register(Banner)
class BannerAdmin(BaseModelAdmin):
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
