from django.contrib import admin
from django.utils.html import format_html

from apps.home.models import CustomerSatisfaction


@admin.register(CustomerSatisfaction)
class CustomerSatisfactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "image_preview",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active",)
    readonly_fields = ("image_preview", "created_at")

    exclude = ("creator",)

    @admin.display(description="تصویر")
    def image_preview(self, obj):
        if not obj.image:
            return "-"

        return format_html(
            '<img src="{}" style="max-height:150px; max-width:250px; '
            'object-fit:contain; border-radius:8px;" />',
            obj.image.url,
        )
