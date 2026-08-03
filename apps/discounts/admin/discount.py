from django.contrib import admin
from django.utils import timezone

from apps.discounts.models import (
    Discount,
    DiscountUsage,
)
from apps.shared.admin import BaseModelAdmin


@admin.register(Discount)
class DiscountAdmin(BaseModelAdmin):

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
            "General",
            {
                "fields": (
                    "code",
                    "discount_type",
                    "value",
                    "is_active",
                )
            },
        ),
        (
            "Limits",
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
            "Time",
            {
                "fields": (
                    "starts_at",
                    "expires_at",
                )
            },
        ),
        (
            "System",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    @admin.display(
        boolean=True,
        description="Valid"
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

    autocomplete_fields = (
        "discount",
        "user",
        "order",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )