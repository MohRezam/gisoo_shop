from django.contrib import admin
from django.utils import timezone

from apps.discounts.models import (
    Discount,
    DiscountUsage,
)


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "discount_type",
        "value",
        "minimum_order_amount",
        "usage_limit",
        "used_count",
        "is_active",
        "is_valid",
        "starts_at",
        "expires_at",
    )

    list_filter = (
        "discount_type",
        "is_active",
        "starts_at",
        "expires_at",
    )

    search_fields = (
        "code",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "used_count",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "عمومی",
            {
                "fields": (
                    "code",
                    "discount_type",
                    "value",
                    "applies_to_discounted_products",
                    "is_active",
                )
            },
        ),
        (
            "محدودیت‌ها",
            {
                "fields": (
                    "minimum_order_amount",
                    "maximum_discount_amount",
                    "usage_limit",
                    "per_user_limit",
                    "used_count",
                )
            },
        ),
        (
            "بازه زمانی",
            {
                "fields": (
                    "starts_at",
                    "expires_at",
                )
            },
        ),
        (
            "سیستم",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
    exclude = ("creator",)
    list_per_page = 15
    show_full_result_count = False

    @admin.display(
        boolean=True,
        description="معتبر"
    )
    def is_valid(
            self,
            obj,
    ):
        now = timezone.now()

        return (
                obj.is_active
                and obj.starts_at <= now <= obj.expires_at
        )


@admin.register(DiscountUsage)
class DiscountUsageAdmin(admin.ModelAdmin):
    list_display = (
        "discount",
        "user",
        "order",
        "created_at",
    )

    search_fields = (
        "discount__code",
        "user__phone_number",
        "user__email",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )
    exclude = ("creator", "archived")
    raw_id_fields = ("discount", "user", "order")
    list_per_page = 15
