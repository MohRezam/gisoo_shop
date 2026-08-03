from django.contrib import admin

from apps.products.models import Brand
from apps.shared.admin import BaseModelAdmin


@admin.register(Brand)
class BrandAdmin(BaseModelAdmin):
    list_display = (
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
