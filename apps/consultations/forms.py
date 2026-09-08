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

    def clean(self):
        cleaned_data = super().clean()

        variant = cleaned_data.get("variant")

        if variant and bundle:
            raise forms.ValidationError(
                "فقط یکی از محصول یا پک را انتخاب کنید."
            )



        return cleaned_data