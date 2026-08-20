from apps.products.models import HairProblem, HairType
from django.contrib import admin


@admin.register(HairProblem)
class HairProblemAdmin(admin.ModelAdmin):
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
    exclude = ("creator",)


@admin.register(HairType)
class HairTypeAdmin(admin.ModelAdmin):
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
    exclude = ("creator",)

