from django.contrib import admin

from apps.products.models import Category
from apps.shared.admin import BaseModelAdmin


@admin.register(Category)
class CategoryAdmin(BaseModelAdmin):
    list_display = (
        "title",
        "parent",
        "created_at",
    )

    list_filter = (
        "created_at",
    )

    search_fields = (
        "title",
        "slug",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }


