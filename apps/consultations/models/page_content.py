from django.db import models

from apps.shared.models.base import BaseModel
from core_gisoo_backend.storage_backends.locations import (
    consultation_page_image_path,
)


class ConsultationPageSection(models.TextChoices):
    INTRO = "intro", "معرفی بالای صفحه (متن کنار عکس)"
    CTA = "cta", "بخش پایین صفحه (متن و عکس)"


class ConsultationPageBlock(BaseModel):
    """
    Editable content blocks for /consult (images + side texts).
    At most one active row per section is intended; admin enforces uniqueness.
    """

    section = models.CharField(
        max_length=20,
        choices=ConsultationPageSection.choices,
        unique=True,
        verbose_name="بخش",
        help_text=(
            "intro = عنوان/توضیح/عکس بالای فرم؛ "
            "cta = عنوان/توضیح/عکس پایین صفحه."
        ),
    )

    title = models.CharField(
        max_length=255,
        verbose_name="عنوان",
    )

    description = models.TextField(
        verbose_name="متن کنار عکس",
    )

    image = models.ImageField(
        upload_to=consultation_page_image_path(),
        verbose_name="تصویر",
        help_text=(
            "intro: حدود ۱۲۰۰×۹۰۰ (نسبت ۴:۳). "
            "cta: حدود ۱۹۲۰×۷۷۰ (نسبت حدود ۵:۲)."
        ),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    class Meta:
        verbose_name = "محتوای صفحه مشاوره"
        verbose_name_plural = "محتوای صفحه مشاوره"
        ordering = ["section"]

    def __str__(self):
        return f"{self.get_section_display()} — {self.title}"
