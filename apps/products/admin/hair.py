from apps.products.models import HairProblem, HairType
from django.contrib import admin


@admin.register(HairProblem)
class HairProblemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "slug",
        "display_order",
        "is_active",
    )
    list_filter = (
        "is_active",
    )
    list_editable = (
        "display_order",
        "is_active",
    )
    search_fields = (
        "title",
        "slug",
    )
    ordering = (
        "display_order",
        "title",
    )
    prepopulated_fields = {
        "slug": ("title",),
    }
    exclude = ("creator", "archived")
    list_per_page = 15
    list_display_links = ("title",)


@admin.register(HairType)
class HairTypeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "slug",
        "is_active",
    )
    list_filter = (
        "is_active",
    )
    search_fields = (
        "title",
        "slug",
    )
    prepopulated_fields = {
        "slug": ("title",),
    }
    exclude = ("creator", "archived")
    list_per_page = 15
    list_display_links = ("title",)
