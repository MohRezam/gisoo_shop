from django.contrib import admin

from apps.consultations.models.consultation import ConsultationRecommendation, ConsultationRequest


class ConsultationRecommendationInline(
    admin.TabularInline
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
        "status",
        "gender",
        "duration",
        "hair_problem",
        "request_phone_consultation"
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
        "user",
        "guest",
        "hair_problem",
    )

    inlines = (
        ConsultationRecommendationInline,
    )

    @admin.display(
        description="Owner"
    )
    def owner(self, obj):
        if obj.user_id:
            return str(obj.user)

        if obj.guest_id:
            return f"Guest ({obj.phone_number})"

        return "-"
