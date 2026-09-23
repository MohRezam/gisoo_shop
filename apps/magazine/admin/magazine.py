from django.contrib import admin

from apps.magazine.models import MagazineCategory, Magazine
from apps.shared.admin_filters import (
    PersianBooleanFilter,
    PersianRelatedFilter,
)


@admin.register(MagazineCategory)
class MagazineCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "slug",
    )
    search_fields = (
        "name",
    )
    prepopulated_fields = {
        "slug": ("name",),
    }
    exclude = ("creator", "archived")
    list_per_page = 15
    list_display_links = ("name",)


@admin.register(Magazine)
class MagazineAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "category",
        "published_at",
        "is_published",
        "is_featured",
        "reading_time",
    )

    list_filter = (
        ("category", PersianRelatedFilter),
        ("is_published", PersianBooleanFilter),
        ("is_featured", PersianBooleanFilter),
    )

    search_fields = (
        "title",
        "short_description",
        "content",
    )

    prepopulated_fields = {
        "slug": ("title",),
    }

    raw_id_fields = (
        "category",
        "related_products",
        "related_articles",
    )

    exclude = ("creator", "archived")
    list_per_page = 15
    list_display_links = ("title",)

    fieldsets = (
        (
            "محتوای مقاله",
            {
                "fields": (
                    "title",
                    "slug",
                    "category",
                    "short_description",
                    "content",
                    "thumbnail",
                ),
                "description": "عنوان، متن و تصویر اصلی مقاله را اینجا وارد کنید.",
            },
        ),
        (
            "انتشار",
            {
                "fields": (
                    "published_at",
                    "is_published",
                    "is_featured",
                    "reading_time",
                ),
                "description": "زمان انتشار و وضعیت نمایش در سایت.",
            },
        ),
        (
            "ارتباطات",
            {
                "classes": ("collapse",),
                "fields": (
                    "related_products",
                    "related_articles",
                ),
                "description": "محصولات و مقالات مرتبط برای پیشنهاد به کاربر.",
            },
        ),
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
