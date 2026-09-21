from django.contrib import admin

from apps.consultations.forms import (
    ConsultationRecommendationAdminForm,
)
from apps.consultations.models.consultation import (
    ConsultationRecommendation,
    ConsultationRecommendationPack,
    ConsultationRecommendationPackItem,
    ConsultationRequest,
)
from apps.shared.admin_filters import (
    PersianBooleanFilter,
    PersianChoicesFilter,
    PersianRelatedFilter,
)


class ConsultationRecommendationInline(
    admin.TabularInline
):
    model = ConsultationRecommendation

    form = ConsultationRecommendationAdminForm

    extra = 0

    fields = (
        "variant",
        "explanation",
        "usage_instruction",
        "display_order",
    )
    raw_id_fields = ("variant",)
    verbose_name = "پیشنهاد محصول"
    verbose_name_plural = "پیشنهادهای محصول"


class ConsultationRecommendationPackItemInline(
    admin.TabularInline
):
    model = ConsultationRecommendationPackItem
    extra = 0
    fields = (
        "recommendation",
        "display_order",
    )
    raw_id_fields = ("recommendation",)
    verbose_name = "آیتم پک"
    verbose_name_plural = "آیتم‌های پک"


@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(
    admin.ModelAdmin
):
    list_display = (
        "full_name",
        "phone_number",
        "hair_problem",
        "gender",
        "duration",
        "status",
        "request_phone_consultation",
        "owner",
        "created_at",
    )

    list_filter = (
        ("status", PersianChoicesFilter),
        ("gender", PersianChoicesFilter),
        ("duration", PersianChoicesFilter),
        ("hair_problem", PersianRelatedFilter),
        ("request_phone_consultation", PersianBooleanFilter),
    )

    search_fields = (
        "full_name",
        "phone_number",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    raw_id_fields = ("user", "guest", "hair_problem")
    list_per_page = 15

    inlines = (
        ConsultationRecommendationInline,
    )

    fieldsets = (
        (
            "اطلاعات درخواست",
            {
                "fields": (
                    "full_name",
                    "phone_number",
                    "gender",
                    "hair_problem",
                    "duration",
                    "status",
                    "request_phone_consultation",
                ),
            },
        ),
        (
            "مالک",
            {
                "fields": (
                    "user",
                    "guest",
                ),
            },
        ),
        (
            "سیستم",
            {
                "fields": (
                    "id",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    @admin.display(
        description="مالک"
    )
    def owner(self, obj):
        if obj.user_id:
            return str(obj.user)

        if obj.guest_id:
            return f"مهمان ({obj.phone_number})"

        return "-"


@admin.register(ConsultationRecommendationPack)
class ConsultationRecommendationPackAdmin(
    admin.ModelAdmin
):
    list_display = (
        "title",
        "consultation",
        "display_order",
        "created_at",
    )
    search_fields = (
        "title",
        "consultation__full_name",
        "consultation__phone_number",
    )
    list_filter = (
        ("consultation", PersianRelatedFilter),
    )
    raw_id_fields = ("consultation",)
    list_editable = ("display_order",)
    list_per_page = 15
    inlines = (
        ConsultationRecommendationPackItemInline,
    )


@admin.register(ConsultationRecommendationPackItem)
class ConsultationRecommendationPackItemAdmin(
    admin.ModelAdmin
):
    list_display = (
        "pack",
        "recommendation",
        "display_order",
        "created_at",
    )
    search_fields = (
        "pack__title",
        "recommendation__variant__sku",
    )
    raw_id_fields = ("pack", "recommendation")
    list_editable = ("display_order",)
    list_per_page = 15
