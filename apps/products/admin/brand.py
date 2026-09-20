from django.contrib import admin

from apps.products.models import Brand


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "created_at",
    )

    search_fields = (
        "title",
        "slug",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }
    exclude = ("creator", "archived")
    list_per_page = 15
    list_display_links = ("title",)
