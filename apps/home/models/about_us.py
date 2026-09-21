from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shared.models.base import BaseModel
from core_gisoo_backend.storage_backends.locations import home_about_image_path


class AboutSection(models.TextChoices):
    INTRO = "intro", _("معرفی (صفحه اصلی و درباره ما)")
    STORY = "story", _("داستان شکل‌گیری")
    CTA = "cta", _("دعوت به اقدام")


class HomeAbout(BaseModel):
    section = models.CharField(
        max_length=20,
        choices=AboutSection.choices,
        default=AboutSection.INTRO,
        verbose_name=_("section"),
        help_text=_(
            "intro = homepage + about first block; "
            "story / cta = about page second and third blocks."
        ),
    )

    title = models.CharField(
        max_length=255,
        verbose_name=_("title"),
    )

    description = models.TextField(
        verbose_name=_("description"),
    )

    image = models.ImageField(
        upload_to=home_about_image_path(),
        verbose_name=_("image"),
    )

    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("display order"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("is active"),
    )

    class Meta:
        verbose_name = "درباره ما"
        verbose_name_plural = "درباره ما"
        ordering = ["display_order", "-created_at"]

    def __str__(self):
        return f"{self.get_section_display()} — {self.title}"
