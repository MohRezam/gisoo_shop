from django.contrib import admin, messages
from django.utils.html import format_html
from jalali_date import datetime2jalali

from apps.notifications.cache import invalidate_unread_count
from apps.notifications.models import AdminAlert, InAppNotification, InAppNotificationType
from apps.shared.admin import BaseModelAdmin
from apps.shared.admin_filters import PersianBooleanFilter, PersianChoicesFilter


TYPE_BADGE_STYLES = {
    InAppNotificationType.ORDER: ("#173ded", "#eef3ff"),
    InAppNotificationType.OFFER: ("#b45309", "#fff7ed"),
    InAppNotificationType.STOCK: ("#0f766e", "#ecfdf5"),
    InAppNotificationType.SYSTEM: ("#475569", "#f1f5f9"),
}


@admin.action(description="علامت‌گذاری به‌عنوان خوانده‌شده")
def mark_as_read(modeladmin, request, queryset):
    user_ids = set()
    updated = 0
    for obj in queryset.filter(is_read=False).only("id", "user_id"):
        user_ids.add(obj.user_id)
        updated += 1
    queryset.filter(is_read=False).update(is_read=True)
    for user_id in user_ids:
        if user_id:
            invalidate_unread_count(user_id)
    modeladmin.message_user(
        request,
        f"{updated} اعلان به‌عنوان خوانده‌شده علامت خورد.",
        messages.SUCCESS,
    )


@admin.action(description="علامت‌گذاری به‌عنوان خوانده‌نشده")
def mark_as_unread(modeladmin, request, queryset):
    user_ids = set()
    updated = 0
    for obj in queryset.filter(is_read=True).only("id", "user_id"):
        user_ids.add(obj.user_id)
        updated += 1
    queryset.filter(is_read=True).update(is_read=False)
    for user_id in user_ids:
        if user_id:
            invalidate_unread_count(user_id)
    modeladmin.message_user(
        request,
        f"{updated} اعلان به‌عنوان خوانده‌نشده علامت خورد.",
        messages.SUCCESS,
    )


@admin.register(InAppNotification)
class InAppNotificationAdmin(BaseModelAdmin):
    change_list_template = "admin/notifications/inappnotification/change_list.html"
    change_form_template = "admin/notifications/inappnotification/change_form.html"

    list_display = (
        "id",
        "title_preview",
        "user_display",
        "type_badge",
        "read_badge",
        "order_link",
        "created_at_fa",
    )
    list_display_links = ("id", "title_preview")
    list_filter = (
        ("type", PersianChoicesFilter),
        ("is_read", PersianBooleanFilter),
        "created_at",
    )
    search_fields = (
        "title",
        "body",
        "user__phone_number",
        "user__first_name",
        "user__last_name",
        "order__public_number",
    )
    raw_id_fields = ("user", "order")
    readonly_fields = ("created_at_fa", "updated_at_fa")
    actions = (mark_as_read, mark_as_unread)
    list_per_page = 25
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    fieldsets = (
        (
            "گیرنده و نوع",
            {
                "description": "اعلان برای کدام کاربر ارسال شود و در کدام دسته اینباکس دیده شود.",
                "fields": (
                    "user",
                    "type",
                    "is_read",
                ),
            },
        ),
        (
            "متن اعلان",
            {
                "description": "عنوان کوتاه و متن کامل پیام که کاربر در اپ می‌بیند.",
                "fields": (
                    "title",
                    "body",
                ),
            },
        ),
        (
            "لینک و سفارش مرتبط",
            {
                "description": "اختیاری — با لمس اعلان، کاربر به این آدرس یا جزئیات سفارش هدایت می‌شود.",
                "fields": (
                    "link",
                    "order",
                    "expires_at",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "اطلاعات سیستم",
            {
                "fields": (
                    "created_at_fa",
                    "updated_at_fa",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    class Media:
        css = {
            "all": ("admin/css/gisoo_admin_notifications.css",),
        }

    @admin.display(description="عنوان", ordering="title")
    def title_preview(self, obj):
        title = (obj.title or "—").strip()
        body = (obj.body or "").strip()
        snippet = body[:72] + ("…" if len(body) > 72 else "")
        if snippet:
            return format_html(
                '<span class="gisoo-notif-title">{}</span>'
                '<span class="gisoo-notif-snippet">{}</span>',
                title,
                snippet,
            )
        return format_html('<span class="gisoo-notif-title">{}</span>', title)

    @admin.display(description="کاربر", ordering="user")
    def user_display(self, obj):
        user = obj.user
        if not user:
            return "—"
        name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        phone = getattr(user, "phone_number", None) or str(user)
        if name:
            return format_html(
                '<span class="gisoo-notif-user"><strong>{}</strong><small>{}</small></span>',
                name,
                phone,
            )
        return format_html('<span class="gisoo-notif-user"><strong>{}</strong></span>', phone)

    @admin.display(description="نوع", ordering="type")
    def type_badge(self, obj):
        label = obj.get_type_display()
        fg, bg = TYPE_BADGE_STYLES.get(obj.type, ("#475569", "#f1f5f9"))
        return format_html(
            '<span class="gisoo-notif-badge" style="color:{};background:{}">{}</span>',
            fg,
            bg,
            label,
        )

    @admin.display(description="وضعیت", ordering="is_read", boolean=False)
    def read_badge(self, obj):
        if obj.is_read:
            return format_html(
                '<span class="gisoo-notif-badge gisoo-notif-badge--read">خوانده‌شده</span>'
            )
        return format_html(
            '<span class="gisoo-notif-badge gisoo-notif-badge--unread">خوانده‌نشده</span>'
        )

    @admin.display(description="سفارش", ordering="order")
    def order_link(self, obj):
        if not obj.order_id:
            return "—"
        order = obj.order
        label = getattr(order, "public_number", None) or f"#{order.pk}"
        try:
            from django.urls import reverse

            url = reverse("admin:orders_order_change", args=[order.pk])
            return format_html('<a class="gisoo-notif-order" href="{}">{}</a>', url, label)
        except Exception:
            return label

    @admin.display(description="زمان ایجاد", ordering="created_at")
    def created_at_fa(self, obj):
        if not obj.created_at:
            return "—"
        try:
            return datetime2jalali(obj.created_at).strftime("%Y/%m/%d - %H:%M")
        except Exception:
            return obj.created_at.strftime("%Y-%m-%d %H:%M")

    @admin.display(description="آخرین ویرایش")
    def updated_at_fa(self, obj):
        if not obj.updated_at:
            return "—"
        try:
            return datetime2jalali(obj.updated_at).strftime("%Y/%m/%d - %H:%M")
        except Exception:
            return obj.updated_at.strftime("%Y-%m-%d %H:%M")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.user_id:
            invalidate_unread_count(obj.user_id)

    def delete_model(self, request, obj):
        user_id = obj.user_id
        super().delete_model(request, obj)
        if user_id:
            invalidate_unread_count(user_id)

    def delete_queryset(self, request, queryset):
        user_ids = {obj.user_id for obj in queryset if obj.user_id}
        super().delete_queryset(request, queryset)
        for user_id in user_ids:
            invalidate_unread_count(user_id)


@admin.register(AdminAlert)
class AdminAlertAdmin(BaseModelAdmin):
    list_display = ["id", "title", "type", "is_read", "created_at"]
    list_filter = [
        ("type", PersianChoicesFilter),
        ("is_read", PersianBooleanFilter),
        "created_at",
    ]
    list_editable = ["is_read"]
    search_fields = ["title", "body"]
    readonly_fields = ["created_at", "updated_at"]
    list_per_page = 25
