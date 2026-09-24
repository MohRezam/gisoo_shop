import nested_admin
from django.contrib import admin

from apps.consultations.forms import (
    ConsultationRecommendationAdminForm,
    ConsultationRecommendationPackItemAdminForm,
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
    nested_admin.NestedTabularInline,
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
    verbose_name_plural = (
        "۱) پیشنهادهای محصول "
        "(توضیح و روش مصرف هر محصول — اختیاری اگر فقط در گروه اضافه می‌کنید)"
    )


class ConsultationRecommendationPackItemInline(
    nested_admin.NestedTabularInline,
):
    model = ConsultationRecommendationPackItem
    form = ConsultationRecommendationPackItemAdminForm
    extra = 1
    fields = (
        "variant",
        "display_order",
    )
    verbose_name = "محصول داخل گروه"
    verbose_name_plural = (
        "محصولات این گروه "
        "(واریانت را مستقیم انتخاب کنید — نیازی به ذخیرهٔ قبلی نیست)"
    )


class ConsultationRecommendationPackInline(
    nested_admin.NestedStackedInline,
):
    model = ConsultationRecommendationPack
    extra = 0
    fields = (
        "title",
        "description",
        "display_order",
    )
    inlines = (
        ConsultationRecommendationPackItemInline,
    )
    verbose_name = "گروه / روتین"
    verbose_name_plural = (
        "۲) گروه‌بندی محصولات "
        "(عنوان و متن مشترک + انتخاب واریانت‌ها در همین ذخیره)"
    )


@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(
    nested_admin.NestedModelAdmin,
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
    list_select_related = ("user", "guest", "hair_problem")
    list_per_page = 15
    show_full_result_count = False

    # Recommendations before packs so same-save get_or_create finds
    # explanations already written in section 1.
    inlines = (
        ConsultationRecommendationInline,
        ConsultationRecommendationPackInline,
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
                "description": (
                    "پیشنهاد تکی و گروه را می‌توانید در همان ذخیره بسازید. "
                    "در بخش گروه، واریانت محصول را مستقیم انتخاب کنید "
                    "(دیگر لازم نیست اول ذخیره کنید و برگردید). "
                    "اگر برای محصول توضیح/دستور مصرف می‌خواهید، "
                    "همان واریانت را در بخش ۱ هم پر کنید."
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


@admin.register(ConsultationRecommendation)
class ConsultationRecommendationAdmin(admin.ModelAdmin):
    """Managed via ConsultationRequest inlines; hidden from sidebar."""

    list_display = (
        "consultation",
        "variant",
        "display_order",
        "created_at",
    )
    search_fields = (
        "consultation__full_name",
        "consultation__phone_number",
        "variant__sku",
        "variant__product__title",
    )
    raw_id_fields = ("consultation", "variant")
    list_per_page = 15

    def has_module_permission(self, request):
        return False


@admin.register(ConsultationRecommendationPack)
class ConsultationRecommendationPackAdmin(admin.ModelAdmin):
    """Managed via ConsultationRequest inlines; hidden from sidebar."""

    list_display = (
        "title",
        "consultation",
        "display_order",
        "created_at",
    )
    search_fields = (
        "title",
        "description",
        "consultation__full_name",
        "consultation__phone_number",
    )
    raw_id_fields = ("consultation",)
    list_per_page = 15

    def has_module_permission(self, request):
        return False


@admin.register(ConsultationRecommendationPackItem)
class ConsultationRecommendationPackItemAdmin(
    admin.ModelAdmin,
):
    """Managed via ConsultationRequest inlines; hidden from sidebar."""

    list_display = (
        "pack",
        "recommendation",
        "display_order",
        "created_at",
    )
    raw_id_fields = ("pack", "recommendation")
    list_per_page = 15

    def has_module_permission(self, request):
        return False
