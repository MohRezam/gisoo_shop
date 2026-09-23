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
    verbose_name_plural = (
        "۱) پیشنهادهای محصول "
        "(توضیح و روش مصرف هر محصول)"
    )


class ConsultationRecommendationPackItemInline(
    admin.TabularInline
):
    model = ConsultationRecommendationPackItem
    extra = 0
    fields = (
        "recommendation",
        "display_order",
    )
    autocomplete_fields = ("recommendation",)
    verbose_name = "محصول داخل گروه"
    verbose_name_plural = "محصولات این گروه"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name != "recommendation":
            return field

        pack_id = request.resolver_match.kwargs.get("object_id") if request.resolver_match else None
        consultation_id = None
        if pack_id:
            consultation_id = (
                ConsultationRecommendationPack.objects
                .filter(pk=pack_id)
                .values_list("consultation_id", flat=True)
                .first()
            )
        elif request.method == "GET":
            consultation_id = request.GET.get("consultation")

        if consultation_id and field is not None:
            field.queryset = ConsultationRecommendation.objects.filter(
                consultation_id=consultation_id,
            ).select_related("variant", "variant__product")
        return field


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
        "packs_help",
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
            "گروه‌بندی پیشنهادها",
            {
                "fields": ("packs_help",),
                "description": (
                    "ابتدا محصولات را با توضیح و روش مصرف در اینلاین پایین اضافه کنید، "
                    "سپس از بخش «گروه‌های پیشنهاد محصول» یک گروه بسازید و محصولات را "
                    "به آن وصل کنید. متن کلی گروه (مثلاً توصیه روتین) در همانجا نوشته می‌شود."
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

    @admin.display(description="راهنما")
    def packs_help(self, obj):
        if not obj or not obj.pk:
            return "پس از ذخیره درخواست، می‌توانید گروه بسازید."
        count = obj.recommendation_packs.count()
        return (
            f"{count} گروه ثبت‌شده — "
            "از منوی «گروه‌های پیشنهاد محصول» گروه جدید بسازید و مشاوره را انتخاب کنید."
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


@admin.register(ConsultationRecommendationPack)
class ConsultationRecommendationPackAdmin(
    admin.ModelAdmin
):
    list_display = (
        "title_or_note",
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
    list_filter = (
        ("consultation", PersianRelatedFilter),
    )
    autocomplete_fields = ("consultation",)
    list_editable = ("display_order",)
    list_per_page = 15
    inlines = (
        ConsultationRecommendationPackItemInline,
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "consultation",
                    "title",
                    "description",
                    "display_order",
                ),
                "description": (
                    "متن کلی گروه برای همه محصولات این گروه نمایش داده می‌شود. "
                    "توضیح و روش مصرف هر محصول را در پیشنهاد محصول مربوطه بنویسید."
                ),
            },
        ),
    )

    @admin.display(description="عنوان / متن گروه")
    def title_or_note(self, obj):
        if obj.title.strip():
            return obj.title
        note = (obj.description or "").strip()
        return (note[:60] + "…") if len(note) > 60 else (note or "—")


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
        "pack__description",
        "recommendation__variant__sku",
        "recommendation__variant__product__title",
    )
    raw_id_fields = ("pack", "recommendation")
    list_editable = ("display_order",)
    list_per_page = 15
