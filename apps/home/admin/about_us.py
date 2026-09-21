from django.contrib import admin

from apps.home.models import HomeAbout


@admin.register(HomeAbout)
class HomeAboutAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "section",
        "title",
        "display_order",
        "is_active",
        "created_at",
    )

    list_filter = (
        "section",
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
    exclude = ("creator", "archived")
    list_per_page = 15
    list_display_links = ("title",)
