from django.contrib import admin
from django.shortcuts import redirect

from apps.payments.models import PaymentGuideVideo


@admin.register(PaymentGuideVideo)
class PaymentGuideVideoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "is_active",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "video",
                    "external_url",
                    "poster",
                    "is_active",
                ),
                "description": (
                    "ویدیوی نمایش‌داده‌شده در صفحه کارت‌به‌کارت "
                    "(دکمه «آموزش پرداخت آسان»). "
                    "می‌توانید فایل mp4 آپلود کنید، یا لینک مستقیم فایل، "
                    "یا لینک صفحه آپارات / یوتیوب را در فیلد URL بگذارید."
                ),
            },
        ),
    )

    def has_add_permission(self, request):
        return not PaymentGuideVideo.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = PaymentGuideVideo.objects.first()
        if obj is not None:
            return redirect(
                f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
                obj.pk,
            )
        return super().changelist_view(request, extra_context=extra_context)
