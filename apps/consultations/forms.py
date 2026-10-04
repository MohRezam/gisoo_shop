from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import ForeignKeyRawIdWidget

from apps.consultations.models.consultation import (
    ConsultationRecommendation,
    ConsultationRecommendationPack,
    ConsultationRecommendationPackItem,
)
from apps.products.models import ProductVariant


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


class ConsultationRecommendationPackItemAdminForm(
    forms.ModelForm
):
    """
    Pack items pick a product variant (not a saved recommendation).

    On save we get_or_create the consultation recommendation so packs and
    products can be created in one admin save — no round-trip required.
    """

    variant = forms.ModelChoiceField(
        label="واریانت محصول",
        queryset=ProductVariant.objects.select_related(
            "product",
        ),
        required=True,
        help_text=(
            "محصول گروه را اینجا با شناسه واریانت انتخاب کنید. "
            "اگر هنوز در لیست پیشنهادها نباشد، هم‌زمان ساخته می‌شود."
        ),
    )

    class Meta:
        model = ConsultationRecommendationPackItem
        fields = (
            "display_order",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        rel = ConsultationRecommendation._meta.get_field(
            "variant",
        ).remote_field
        self.fields["variant"].widget = ForeignKeyRawIdWidget(
            rel=rel,
            admin_site=admin.site,
        )
        recommendation_id = getattr(
            self.instance,
            "recommendation_id",
            None,
        )
        if recommendation_id:
            self.fields["variant"].initial = (
                self.instance.recommendation.variant_id
            )

    def _consultation_id(self):
        pack = getattr(self.instance, "pack", None)
        if pack is not None and pack.consultation_id:
            return pack.consultation_id
        pack_id = getattr(self.instance, "pack_id", None)
        if not pack_id:
            return None
        return (
            ConsultationRecommendationPack.objects
            .filter(pk=pack_id)
            .values_list("consultation_id", flat=True)
            .first()
        )

    def clean(self):
        cleaned = super().clean()
        variant = cleaned.get("variant")
        if not variant:
            return cleaned

        consultation_id = self._consultation_id()
        if consultation_id is None:
            # Parent pack FK is assigned just before save; validate then.
            return cleaned

        return cleaned

    def save(self, commit=True):
        variant = self.cleaned_data["variant"]
        instance = super().save(commit=False)

        consultation_id = self._consultation_id()
        if consultation_id is None:
            raise forms.ValidationError(
                "ابتدا گروه را ذخیره کنید یا درخواست مشاوره معتبر باشد."
            )

        recommendation, _created = (
            ConsultationRecommendation.objects.get_or_create(
                consultation_id=consultation_id,
                variant=variant,
                defaults={
                    "display_order": (
                        self.cleaned_data.get("display_order")
                        or 0
                    ),
                },
            )
        )
        instance.recommendation = recommendation

        if commit:
            instance.save()
            self.save_m2m()
        return instance
