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
            "product",
            "bundle",
            "explanation",
            "usage_instruction",
            "display_order",
        )

    def clean(self):
        cleaned_data = super().clean()

        product = cleaned_data.get("product")
        bundle = cleaned_data.get("bundle")

        if product and bundle:
            raise forms.ValidationError(
                "فقط یکی از محصول یا پک را انتخاب کنید."
            )

        if not product and not bundle:
            raise forms.ValidationError(
                "باید یک محصول یا یک پک انتخاب کنید."
            )

        return cleaned_data