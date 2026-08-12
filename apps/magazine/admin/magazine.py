from django.contrib import admin

from apps.magazine.models import MagazineCategory, Magazine
from apps.shared.admin import BaseModelAdmin


@admin.register(MagazineCategory)
class MagazineCategoryAdmin(BaseModelAdmin):
    list_display = (
        "name",
        "slug",
    )
    search_fields = (
        "name",
    )
    prepopulated_fields = {
        "slug": ("name",),
    }


@admin.register(Magazine)
class MagazineAdmin(BaseModelAdmin):
    list_display = (
        "title",
        "category",
        "published_at",
        "is_published",
    )

    list_filter = (
        "category",
        "is_published",
        "published_at",
    )

    search_fields = (
        "title",
        "short_description",
        "content",
    )

    prepopulated_fields = {
        "slug": ("title",),
    }

    filter_horizontal = (
        "related_products",
        "related_articles",
    )

    autocomplete_fields = (
        "category",
    )

    def save_model(self, request, obj, form, change):
        if obj.is_featured:
            Magazine.objects.exclude(
                pk=obj.pk
            ).filter(
                is_featured=True
            ).update(
                is_featured=False
            )

        super().save_model(request, obj, form, change)
