from django.contrib import admin
from django.shortcuts import redirect
from django.utils.safestring import mark_safe

from apps.notifications.models import SmsSettings


@admin.register(SmsSettings)
class SmsSettingsAdmin(admin.ModelAdmin):
    change_form_template = "admin/notifications/smssettings/change_form.html"

    fieldsets = (
        (
            "پیامک‌های سفارش و پرداخت",
            {
                "classes": ("gisoo-sms-fieldset",),
                "description": mark_safe(
                    '<p class="gisoo-sms-lead">'
                    "با این تیک‌ها مشخص کنید کدام رویدادها پیامک بفرستند. "
                    "پیش‌فرض همه فعال‌اند. سوئیچ کلی <code>SMS_ENABLED</code> در سرور "
                    "هنوز باید روشن باشد."
                    "</p>"
                ),
                "fields": (
                    "sms_order_created",
                    "sms_payment_success",
                    "sms_payment_reminder",
                    "sms_order_shipped",
                    "sms_order_cancelled",
                    "sms_delivery_confirm",
                ),
            },
        ),
        (
            "پیامک‌های مشاوره و محتوا",
            {
                "classes": ("gisoo-sms-fieldset",),
                "fields": (
                    "sms_new_consultation",
                    "sms_new_comment",
                    "sms_new_image",
                ),
            },
        ),
    )

    class Media:
        css = {
            "all": ("admin/css/gisoo_admin_sms_settings.css",),
        }

    def has_add_permission(self, request):
        return not SmsSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = SmsSettings.load()
        return redirect(
            f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
            obj.pk,
        )
