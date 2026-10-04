import nested_admin
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse

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

COMPLETION_REQUIRES_ANSWER_MSG = (
    "وضعیت «تکمیل‌شده» ذخیره نشد. "
    "حداقل یک پیشنهاد محصول یا یک گروه محصول "
    "(با حداقل یک محصول) لازم است."
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
        "(برای تکمیل‌شده شدن، حداقل یک محصول اینجا یا داخل گروه لازم است)"
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
                    "برای وضعیت «تکمیل‌شده» حداقل یک پیشنهاد محصول "
                    "یا یک گروه محصول با حداقل یک محصول الزامی است. "
                    "پیشنهاد تکی و گروه را می‌توانید در همان ذخیره بسازید. "
                    "در بخش گروه، واریانت محصول را مستقیم انتخاب کنید. "
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

    def save_model(self, request, obj, form, change):
        self._wants_completed = (
            obj.status == ConsultationRequest.Status.COMPLETED
        )
        self._was_completed = False
        if change and obj.pk:
            self._was_completed = (
                ConsultationRequest.objects.filter(pk=obj.pk)
                .values_list("status", flat=True)
                .first()
                == ConsultationRequest.Status.COMPLETED
            )
        # Defer first-time completion until after inlines are saved,
        # so SMS/signal only fire when an answer actually exists.
        if self._wants_completed and not self._was_completed:
            obj.status = ConsultationRequest.Status.PENDING
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        self._completion_blocked = False
        if not getattr(self, "_wants_completed", False):
            return

        obj = form.instance
        obj.refresh_from_db()

        if obj.has_recommendation_answer():
            if obj.status != ConsultationRequest.Status.COMPLETED:
                obj.status = ConsultationRequest.Status.COMPLETED
                obj.save(update_fields=["status", "updated_at"])
            return

        if obj.status == ConsultationRequest.Status.COMPLETED:
            obj.status = ConsultationRequest.Status.PENDING
            obj.save(update_fields=["status", "updated_at"])

        self._completion_blocked = True
        messages.error(request, COMPLETION_REQUIRES_ANSWER_MSG)

    def response_change(self, request, obj):
        if getattr(self, "_completion_blocked", False):
            self._completion_blocked = False
            return HttpResponseRedirect(request.path)
        return super().response_change(request, obj)

    def response_add(self, request, obj, post_url_continue=None):
        if getattr(self, "_completion_blocked", False):
            self._completion_blocked = False
            opts = self.model._meta
            return HttpResponseRedirect(
                reverse(
                    f"admin:{opts.app_label}_{opts.model_name}_change",
                    args=[obj.pk],
                )
            )
        return super().response_add(
            request,
            obj,
            post_url_continue=post_url_continue,
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
