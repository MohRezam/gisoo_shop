from django.contrib import admin

from apps.consultations.models import ConsultationPageBlock


@admin.register(ConsultationPageBlock)
class ConsultationPageBlockAdmin(admin.ModelAdmin):
    list_display = (
        "section",
        "title",
        "is_active",
        "updated_at",
    )
    list_filter = (
        "section",
        "is_active",
    )
    search_fields = (
        "title",
        "description",
    )
    list_editable = ("is_active",)
    list_display_links = ("title",)
    exclude = ("creator", "archived")
    list_per_page = 15
    fieldsets = (
        (
            "محتوای نمایشی صفحه مشاوره",
            {
                "description": (
                    "برای هر بخش فقط یک رکورد بسازید. "
                    "عنوان و متن کنار عکس، و خود تصویر، در صفحه /consult نمایش داده می‌شوند."
                ),
                "fields": (
                    "section",
                    "title",
                    "description",
                    "image",
                    "is_active",
                ),
            },
        ),
    )

    def has_add_permission(self, request):
        # Only two sections exist; block add when both are present.
        existing = ConsultationPageBlock.objects.values_list(
            "section",
            flat=True,
        )
        return len(set(existing)) < 2
