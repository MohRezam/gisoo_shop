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
)
from apps.orders.services.bulk_tracking_import import (
    build_empty_tracking_template,
    build_preparing_orders_workbook,
    import_tracking_from_workbook,
)
from apps.orders.services.change_order_status import (
    change_order_status,
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
        "original_unit_price",
        "unit_price",
        "total_price",
        "province",
        "city",
        "postal_code",
        "full_address",
        "order_bundle",
    ]
    exclude = ("creator",)
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    change_list_template = "admin/orders/order/change_list.html"

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
        "public_number",
        "user__phone_number",
        "phone_number",
        "tracking_code",
    ]

    readonly_fields = [
        "status",
        "products_price",
        "shipping_price",
        "discount_amount",
        "total_price",
        "created_at",
        "updated_at",
        "expires_at",
    ]

    inlines = [
        OrderItemInline,
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
    list_per_page = 15
    list_display_links = ("user",)

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
                f"{updated} order(s) marked as {label}.",
                level=messages.SUCCESS,
            )

    @admin.action(description="Mark selected as preparing")
    def mark_preparing(self, request, queryset):
        self._bulk_change_status(
            request,
            queryset,
            OrderStatus.PREPARING,
            "preparing",
        )

    @admin.action(description="Mark selected as shipped")
    def mark_shipped(self, request, queryset):
        self._bulk_change_status(
            request,
            queryset,
            OrderStatus.SHIPPED,
            "shipped",
        )

    @admin.action(description="Mark selected as delivered")
    def mark_delivered(self, request, queryset):
        self._bulk_change_status(
            request,
            queryset,
            OrderStatus.DELIVERED,
            "delivered",
        )

    @admin.action(description="Mark selected as canceled")
    def mark_canceled(self, request, queryset):
        self._bulk_change_status(
            request,
            queryset,
            OrderStatus.CANCELED,
            "canceled",
        )
