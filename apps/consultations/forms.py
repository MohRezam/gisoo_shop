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
            "bundle",
            "explanation",
            "usage_instruction",
            "display_order",
        )

    def clean(self):
        cleaned_data = super().clean()

        variant = cleaned_data.get("variant")
        bundle = cleaned_data.get("bundle")

        if variant and bundle:
            raise forms.ValidationError(
                "فقط یکی از محصول یا پک را انتخاب کنید."
            )

        if not variant and not bundle:
            raise forms.ValidationError(
                "حداقل یکی از محصول یا پک را انتخاب کنید."
            )

        return cleaned_data