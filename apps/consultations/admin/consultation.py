from django.contrib import admin

from apps.consultations.models.consultation import ConsultationRecommendation, ConsultationRequest


class ConsultationRecommendationInline(
    admin.TabularInline,
):
    model = ConsultationRecommendation

    extra = 1

    autocomplete_fields = (
        "product",
    )

    fields = (
        "product",
        "explanation",
        "display_order",
    )


@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(
    admin.ModelAdmin,
):
    list_display = (
        "full_name",
        "phone_number",
        "hair_problem",
        "gender",
        "duration",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "gender",
        "duration",
        "hair_problem",
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

    list_select_related = (
        "hair_problem",
    )

    inlines = (
        ConsultationRecommendationInline,
    )