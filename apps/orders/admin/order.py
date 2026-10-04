from datetime import timedelta

from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.orders.admin.forms import BulkTrackingUploadForm
from apps.orders.models import (
    Order,
    OrderItem,
    OrderStatus,
    OrderStatusHistory,
)
from apps.orders.ordering import apply_status_priority_ordering
from apps.orders.services.bulk_tracking_import import (
    build_empty_tracking_template,
    build_preparing_orders_workbook,
    import_tracking_from_workbook,
)
from apps.orders.services.change_order_status import (
    change_order_status,
)
from django_admin_inline_paginator.admin import TabularInlinePaginated

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


class OrderItemInline(TabularInlinePaginated):
    model = OrderItem
    extra = 0
    per_page = 20
    pagination_key = "orderitem_page"
    can_delete = False
    # Address lives on Order — do not repeat on every line item.
    fields = (
        "variant",
        "product_title",
        "variant_sku",
        "quantity",
        "original_unit_price",
        "unit_price",
        "total_price",
        "order_bundle",
    )
    readonly_fields = (
        "variant",
        "product_title",
        "variant_sku",
        "quantity",
        "original_unit_price",
        "unit_price",
        "total_price",
        "order_bundle",
    )
    show_change_link = False
    verbose_name = "آیتم"
    verbose_name_plural = "آیتم‌های سفارش"


class OrderStatusHistoryInline(TabularInlinePaginated):
    model = OrderStatusHistory
    extra = 0
    per_page = 15
    pagination_key = "status_history_page"
    can_delete = False
    ordering = ("-created_at",)
    fields = (
        "created_at",
        "old_status",
        "new_status",
        "changed_by",
        "source",
        "reason",
    )
    readonly_fields = fields
    show_change_link = False
    verbose_name = "تغییر وضعیت"
    verbose_name_plural = "تاریخچه وضعیت سفارش"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("changed_by")
        )

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    change_list_template = "admin/orders/order/change_list.html"

    list_display = [
        "id",
        "user",
        "status",
        "carrier",
        "tracking_code",
        "total_price",
        "phone_number",
        "created_at",
    ]

    list_filter = [
        ("status", PersianChoicesFilter),
        ("carrier", PersianChoicesFilter),
        OrderCreatedAtFilter,
        ("province", PersianAllValuesFilter),
        ("city", PersianAllValuesFilter),
    ]

    search_fields = [
        "id",
        "public_number",
        "user__phone_number",
        "phone_number",
        "tracking_code",
    ]

    readonly_fields = [
        "status",
        "public_number",
        "products_price",
        "shipping_price",
        "discount_amount",
        "total_price",
        "created_at",
        "updated_at",
        "expires_at",
        "payment_reminder_sent_at",
        "payment_reminder_mid_sent_at",
        "delivery_confirm_sms_sent_at",
        "prepared_at",
        "shipped_at",
        "delivered_at",
    ]

    fieldsets = (
        (
            "سفارش و مشتری",
            {
                "fields": (
                    "public_number",
                    "user",
                    "phone_number",
                    "status",
                    "description",
                ),
            },
        ),
        (
            "آدرس تحویل",
            {
                "fields": (
                    "province",
                    "city",
                    "postal_code",
                    "address",
                ),
            },
        ),
        (
            "ارسال",
            {
                "fields": (
                    "shipping_method",
                    "carrier",
                    "tracking_code",
                    "prepared_at",
                    "shipped_at",
                    "delivered_at",
                ),
            },
        ),
        (
            "مبالغ",
            {
                "fields": (
                    "products_price",
                    "shipping_price",
                    "discount",
                    "discount_amount",
                    "total_price",
                ),
            },
        ),
        (
            "سیستم",
            {
                "classes": ("collapse",),
                "fields": (
                    "expires_at",
                    "payment_reminder_sent_at",
                    "payment_reminder_mid_sent_at",
                    "delivery_confirm_sms_sent_at",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    inlines = [
        OrderItemInline,
        OrderStatusHistoryInline,
    ]

    actions = [
        "mark_preparing",
        "mark_shipped",
        "mark_delivered",
        "mark_canceled",
    ]

    ordering = [
        "-created_at",
    ]
    exclude = ("creator", "archived")
    raw_id_fields = ("user", "discount", "shipping_method")
    list_select_related = ("user", "discount", "shipping_method")
    list_per_page = 20
    show_full_result_count = False
    list_display_links = ("user",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return apply_status_priority_ordering(queryset)

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "bulk-tracking/",
                self.admin_site.admin_view(self.bulk_tracking_view),
                name="orders_order_bulk_tracking",
            ),
            path(
                "bulk-tracking/template/",
                self.admin_site.admin_view(self.bulk_tracking_template_view),
                name="orders_order_bulk_tracking_template",
            ),
            path(
                "bulk-tracking/preparing/",
                self.admin_site.admin_view(self.bulk_tracking_preparing_view),
                name="orders_order_bulk_tracking_preparing",
            ),
        ]
        return custom + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["show_bulk_tracking"] = self.has_change_permission(request)
        return super().changelist_view(request, extra_context=extra_context)

    def _require_change_permission(self, request):
        if not self.has_change_permission(request):
            raise PermissionDenied

    def bulk_tracking_view(self, request):
        self._require_change_permission(request)

        import_result = None
        form = BulkTrackingUploadForm()

        if request.method == "POST":
            form = BulkTrackingUploadForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    import_result = import_tracking_from_workbook(
                        file_obj=form.cleaned_data["file"],
                        changed_by=request.user,
                    )
                except ValidationError as exc:
                    form.add_error(
                        None,
                        str(exc.detail if hasattr(exc, "detail") else exc),
                    )
                else:
                    if import_result.success_count:
                        self.message_user(
                            request,
                            f"{import_result.success_count} سفارش با موفقیت به‌روز شد.",
                            level=messages.SUCCESS,
                        )
                    if import_result.errors:
                        self.message_user(
                            request,
                            f"{len(import_result.errors)} ردیف با خطا مواجه شد.",
                            level=messages.WARNING,
                        )
                    elif import_result.success_count == 0:
                        self.message_user(
                            request,
                            "هیچ ردیف معتبری برای اعمال پیدا نشد.",
                            level=messages.WARNING,
                        )

        context = {
            **self.admin_site.each_context(request),
            "title": "ورود کد رهگیری از اکسل",
            "opts": self.model._meta,
            "form": form,
            "import_result": import_result,
            "has_view_permission": self.has_view_permission(request),
            "has_change_permission": self.has_change_permission(request),
        }
        return render(
            request,
            "admin/orders/bulk_tracking_import.html",
            context,
        )

    def bulk_tracking_template_view(self, request):
        self._require_change_permission(request)
        content = build_empty_tracking_template()
        response = HttpResponse(
            content,
            content_type=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
        )
        response["Content-Disposition"] = (
            'attachment; filename="tracking_template.xlsx"'
        )
        return response

    def bulk_tracking_preparing_view(self, request):
        self._require_change_permission(request)
        content = build_preparing_orders_workbook()
        response = HttpResponse(
            content,
            content_type=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
        )
        response["Content-Disposition"] = (
            'attachment; filename="preparing_orders.xlsx"'
        )
        return response

    def _bulk_change_status(self, request, queryset, new_status, label):
        updated = 0
        for order in queryset:
            try:
                change_order_status(
                    order=order,
                    new_status=new_status,
                    changed_by=request.user,
                    reason=f"Changed via admin action ({label}).",
                )
                updated += 1
            except ValidationError as exc:
                self.message_user(
                    request,
                    f"Order #{order.pk}: {exc}",
                    level=messages.ERROR,
                )

        if updated:
            self.message_user(
                request,
                f"{updated} سفارش به وضعیت «{label}» تغییر کرد.",
                level=messages.SUCCESS,
            )

    @admin.action(description="تغییر به در حال آماده‌سازی")
    def mark_preparing(self, request, queryset):
        self._bulk_change_status(
            request,
            queryset,
            OrderStatus.PREPARING,
            "در حال آماده‌سازی",
        )

    @admin.action(description="تغییر به ارسال‌شده")
    def mark_shipped(self, request, queryset):
        """
        Requires tracking_code (and carrier via order/shipping method)
        — enforced in change_order_status.
        """
        self._bulk_change_status(
            request,
            queryset,
            OrderStatus.SHIPPED,
            "ارسال‌شده",
        )

    @admin.action(description="تغییر به تحویل‌شده")
    def mark_delivered(self, request, queryset):
        self._bulk_change_status(
            request,
            queryset,
            OrderStatus.DELIVERED,
            "تحویل‌شده",
        )

    @admin.action(description="لغو سفارش‌های انتخاب‌شده")
    def mark_canceled(self, request, queryset):
        self._bulk_change_status(
            request,
            queryset,
            OrderStatus.CANCELED,
            "لغو شده",
        )
