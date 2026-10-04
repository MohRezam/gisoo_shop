from django.contrib import admin
from django.shortcuts import redirect

from apps.home.models import SocialLinks


@admin.register(SocialLinks)
class SocialLinksAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "telegram_url",
        "instagram_url",
        "whatsapp_url",
        "bale_url",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "telegram_url",
                    "instagram_url",
                    "whatsapp_url",
                    "bale_url",
                ),
                "description": (
                    "لینک‌های نمایش‌داده‌شده در فوتر و صفحه ارتباط با ما. "
                    "مثال واتساپ: https://wa.me/989004553585"
                ),
            },
        ),
    )

    def has_add_permission(self, request):
        return not SocialLinks.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = SocialLinks.objects.first()
        if obj is not None:
            return redirect(
                f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
                obj.pk,
            )
        return super().changelist_view(request, extra_context=extra_context)
