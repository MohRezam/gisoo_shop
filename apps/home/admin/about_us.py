from django.contrib import admin

from apps.home.models import HomeAbout
from apps.shared.admin import BaseModelAdmin


@admin.register(HomeAbout)
class HomeAboutAdmin(BaseModelAdmin):
    list_display = (
        "title",
        "display_order",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "title",
        "description",
    )

    list_editable = (
        "display_order",
        "is_active",
    )

    ordering = (
        "display_order",
        "-created_at",
    )