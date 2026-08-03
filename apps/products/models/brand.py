from apps.shared.models.base import BaseModel
from django.db import models
from django.utils.translation import gettext_lazy as _

from core_gisoo_backend.storage_backends.locations import brand_logos_path


class Brand(BaseModel):
    title = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("title"),
    )

    slug = models.SlugField(
        unique=True,
        verbose_name=_("slug"),
    )

    logo = models.ImageField(
        upload_to=brand_logos_path(),
        verbose_name=_("logo"),
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _("brand")
        verbose_name_plural = _("brands")
        ordering = ["title"]

    def __str__(self):
        return self.title
