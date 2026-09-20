from datetime import timedelta

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils import timezone

from apps.orders.models import (
    Order,
    OrderItem,
)
from apps.shared.admin_filters import (
    PersianAllValuesFilter,
    PersianChoicesFilter,
)


class OrderCreatedAtFilter(SimpleListFilter):
    title = "تاریخ ایجاد"
    parameter_name = "created_range"

    def lookups(self, request, model_admin):
        return (
            ("today", "امروز"),
            ("7days", "۷ روز گذشته"),
            ("month", "این ماه"),
            ("year", "امسال"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset

        today = timezone.localdate()

        if value == "today":
            return queryset.filter(created_at__date=today)
        if value == "7days":
            return queryset.filter(created_at__date__gte=today - timedelta(days=7))
        if value == "month":
            return queryset.filter(
                created_at__year=today.year,
                created_at__month=today.month,
            )
        if value == "year":
            return queryset.filter(created_at__year=today.year)
        return queryset

    def choices(self, changelist):
        yield {
            "selected": self.value() is None,
            "query_string": changelist.get_query_string(remove=[self.parameter_name]),
            "display": "همه",
        }
        for lookup, title in self.lookup_choices:
            yield {
                "selected": self.value() == str(lookup),
                "query_string": changelist.get_query_string(
                    {self.parameter_name: lookup}
                ),
                "display": title,
            }


class OrderItemInline(admin.TabularInline):
    model = OrderItem

    extra = 0

    readonly_fields = [
        "variant",
        "product_title",
        "variant_sku",
        "quantity",
        "unit_price",
        "total_price",
    ]
    exclude = ("creator",)
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "status",
        "total_price",
        "phone_number",
        "created_at",
    ]

    list_filter = [
        ("status", PersianChoicesFilter),
        OrderCreatedAtFilter,
        ("province", PersianAllValuesFilter),
        ("city", PersianAllValuesFilter),
    ]

    search_fields = [
        "id",
        "user__phone_number",
        "receiver_name",
        "phone_number",
        "tracking_code"
    ]

    readonly_fields = [
        "total_price",
        "created_at",
        "updated_at",
        "expires_at",
    ]

    inlines = [
        OrderItemInline,
    ]

    ordering = [
        "-created_at",
    ]
    exclude = ("creator", "archived")
    raw_id_fields = ("user", "discount", "shipping_method")
    list_per_page = 15
    list_display_links = ("user",)
