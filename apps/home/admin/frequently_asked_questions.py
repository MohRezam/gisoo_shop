from django.contrib import admin

from apps.home.models import FAQCategory, FAQ


@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
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
    list_per_page = 15
    list_display_links = ("title",)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = (
        "id",
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

    ordering = (
        "ordering",
        "id",
    )
    exclude = ("creator",)
    raw_id_fields = ("category",)
    list_per_page = 15
    list_display_links = ("question",)
