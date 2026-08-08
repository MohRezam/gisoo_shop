from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shared.models.base import BaseModel
from core_gisoo_backend.storage_backends.locations import home_about_image_path


class HomeAbout(BaseModel):
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
        verbose_name = _("home about")
        verbose_name_plural = _("home abouts")
        ordering = ["display_order", "-created_at"]

    def __str__(self):
        return self.title