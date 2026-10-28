from django.contrib import admin

from apps.reviews.models import ProductReview, ReviewStatus
from apps.reviews.models.review import review_author_label
from apps.shared.admin_filters import (
    PersianBooleanFilter,
    PersianChoicesFilter,
)


class ReviewSourceFilter(admin.SimpleListFilter):
    title = "منبع"
    parameter_name = "source"

    def lookups(self, request, model_admin):
        return (
            ("manual", "دستی"),
            ("customer", "مشتری"),
        )

    def queryset(self, request, queryset):
        if self.value() == "manual":
            return queryset.filter(user__isnull=True)
        if self.value() == "customer":
            return queryset.filter(user__isnull=False)
        return queryset


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "author",
        "rating",
        "status",
        "is_featured",
        "homepage_order",
        "created_at",
    )

    list_filter = (
        ("status", PersianChoicesFilter),
        ReviewSourceFilter,
        ("is_featured", PersianBooleanFilter),
        "rating",
        "created_at",
    )

    search_fields = (
        "product__title",
        "comment",
        "author_name",
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
    list_select_related = ("user", "product")
    list_per_page = 15
    show_full_result_count = False
    list_display_links = ("product",)

    @admin.display(description="نویسنده")
    def author(self, obj):
        return review_author_label(obj)

    def get_changeform_initial_data(self, request):
        return {"status": ReviewStatus.APPROVED}

    fieldsets = (
        (
            "اطلاعات نظر",
            {
                "fields": (
                    "author_name",
                    "user",
                    "product",
                    "rating",
                    "comment",
                ),
                "description": (
                    "برای نظر خودتان فقط نام نویسنده، محصول، امتیاز و متن را پر کنید "
                    "و کاربر را خالی بگذارید. نظر مشتریان به حساب خودشان وصل است."
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
