from apps.products.models import HairProblem, HairType
from apps.shared.admin import BaseModelAdmin
from django.contrib import admin


@admin.register(HairProblem)
class HairProblemAdmin(BaseModelAdmin):
    list_display = (
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


@admin.register(HairType)
class HairTypeAdmin(BaseModelAdmin):
    list_display = (
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
