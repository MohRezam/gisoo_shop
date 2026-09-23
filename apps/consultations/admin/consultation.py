import nested_admin
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


def _consultation_id_from_request(request):
    if not request or not request.resolver_match:
        return None
    return request.resolver_match.kwargs.get("object_id")


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
        "(توضیح و روش مصرف هر محصول)"
    )


class ConsultationRecommendationPackItemInline(
    nested_admin.NestedTabularInline,
):
    model = ConsultationRecommendationPackItem
    extra = 0
    fields = (
        "recommendation",
        "display_order",
    )
    verbose_name = "محصول داخل گروه"
    verbose_name_plural = (
        "محصولات این گروه "
        "(فقط از پیشنهادهای همین درخواست)"
    )

    def formfield_for_foreignkey(
        self,
        db_field,
        request,
        **kwargs,
    ):
        if db_field.name == "recommendation":
            consultation_id = _consultation_id_from_request(
                request,
            )
            if consultation_id:
                kwargs["queryset"] = (
                    ConsultationRecommendation.objects
                    .filter(
                        consultation_id=consultation_id,
                    )
                    .select_related(
                        "variant",
                        "variant__product",
                    )
                    .order_by(
                        "display_order",
                        "created_at",
                    )
                )
            else:
                kwargs["queryset"] = (
                    ConsultationRecommendation.objects.none()
                )
        return super().formfield_for_foreignkey(
            db_field,
            request,
            **kwargs,
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
        "(اختیاری — متن مشترک برای چند محصول)"
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
    list_per_page = 15

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
                    "۱) پایین صفحه محصولات پیشنهادی را اضافه کنید و ذخیره کنید. "
                    "۲) دوباره همین صفحه را باز کنید و در بخش گروه، "
                    "محصولات همین درخواست را به روتین وصل کنید و متن مشترک بنویسید."
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
