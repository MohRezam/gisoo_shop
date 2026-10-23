from django.contrib import admin

from apps.products.models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "display_order",
        "parent",
        "created_at",
    )

    list_editable = (
        "display_order",
    )

    list_filter = (
        "created_at",
    )

    ordering = (
        "display_order",
        "title",
    )

    search_fields = (
        "title",
        "slug",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }
    exclude = ("creator", "archived")
    raw_id_fields = ("parent",)
    list_per_page = 15
    list_display_links = ("title",)
