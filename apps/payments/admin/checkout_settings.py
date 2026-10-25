from django.contrib import admin
from django.shortcuts import redirect

from apps.payments.models import ShopCheckoutSettings


@admin.register(ShopCheckoutSettings)
class ShopCheckoutSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "سقف خرید",
            {
                "fields": (
                    "min_order_amount",
                    "max_order_amount",
                ),
                "description": "۰ یعنی آن محدودیت خاموش است.",
            },
        ),
        (
            "کارت‌به‌کارت",
            {
                "fields": (
                    "payment_expiration_minutes",
                    "support_url",
                    "terms",
                ),
            },
        ),
    )

    def has_add_permission(self, request):
        return not ShopCheckoutSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = ShopCheckoutSettings.objects.first()
        if obj is None:
            obj = ShopCheckoutSettings.objects.create(pk=1)
        return redirect(
            f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
            obj.pk,
        )

    def save_model(self, request, obj, form, change):
        obj.full_clean()
        super().save_model(request, obj, form, change)
