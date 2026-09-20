from django import forms

from apps.consultations.models.consultation import (
    ConsultationRecommendation,
)


class ConsultationRecommendationAdminForm(
    forms.ModelForm
):
    class Meta:
        model = ConsultationRecommendation
        fields = (
            "variant",
            "explanation",
            "usage_instruction",
            "display_order",
        )