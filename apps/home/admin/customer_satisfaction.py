from django.contrib import admin
from django.utils.html import format_html

from apps.home.models import CustomerSatisfaction


@admin.register(CustomerSatisfaction)
class CustomerSatisfactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active",)
    readonly_fields = ("created_at",)

    exclude = ("creator",)
