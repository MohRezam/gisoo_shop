from django.contrib import admin

from apps.reviews.models import ProductReview
from apps.shared.admin_filters import (
    PersianBooleanFilter,
    PersianChoicesFilter,
)


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "user",
        "rating",
        "status",
        "is_featured",
        "homepage_order",
        "created_at",
    )

    list_filter = (
        ("status", PersianChoicesFilter),
        ("is_featured", PersianBooleanFilter),
        "rating",
        "created_at",
    )

    search_fields = (
        "product__title",
        "comment",
        "user__phone_number",
    )

    list_editable = (
        "status",
        "is_featured",
        "homepage_order",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )
    exclude = ("creator", "archived")

    raw_id_fields = ("user", "product")
    list_per_page = 15
    list_display_links = ("product",)

    fieldsets = (
        (
            "اطلاعات نظر",
            {
                "fields": (
                    "user",
                    "product",
                    "rating",
                    "comment",
                ),
            },
        ),
        (
            "وضعیت و نمایش",
            {
                "fields": (
                    "status",
                    "is_featured",
                    "homepage_order",
                ),
                "description": "نظرات ویژه در صفحه اصلی فروشگاه نمایش داده می‌شوند.",
            },
        ),
        (
            "سیستم",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )
