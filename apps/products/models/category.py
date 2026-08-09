from apps.shared.models.base import BaseModel
from django.db import models
from django.utils.translation import gettext_lazy as _

from core_gisoo_backend.storage_backends.locations import category_image_path


class Category(BaseModel):
    title = models.CharField(
        max_length=255,
        verbose_name=_("title"),
    )

    slug = models.SlugField(
        unique=True,
        verbose_name=_("slug"),
    )
    image = models.ImageField(
        upload_to=category_image_path(),
        verbose_name=_("image"),
        null=True,
        blank=True
    )
    short_description = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name=_("short_description"),
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="children",
        verbose_name=_("parent"),
    )

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")
        ordering = ["title"]

    def __str__(self):
        return self.title
