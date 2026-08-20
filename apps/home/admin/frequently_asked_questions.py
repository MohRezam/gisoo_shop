from django.contrib import admin

from apps.home.models import FAQCategory, FAQ


@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "slug",
        "is_active",
        "ordering",
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
    ordering = (
        "ordering",
        "id",
    )
    exclude = ("creator",)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = (
        "question",
        "category",
        "is_active",
        "ordering",
        "created_at",
    )
    list_filter = (
        "category",
        "is_active",
    )
    search_fields = (
        "question",
        "answer",
    )
    list_editable = (
        "is_active",
        "ordering",
    )
    autocomplete_fields = (
        "category",
    )
    ordering = (
        "ordering",
        "id",
    )
    exclude = ("creator",)
