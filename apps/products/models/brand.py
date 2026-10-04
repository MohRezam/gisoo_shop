from apps.shared.models.base import BaseModel
from django.db import models

from core_gisoo_backend.storage_backends.locations import brand_logos_path


class Brand(BaseModel):
    title = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="عنوان",
    )

    slug = models.SlugField(
        unique=True,
        verbose_name="اسلاگ",
    )

    logo = models.ImageField(
        upload_to=brand_logos_path(),
        verbose_name="لوگو",
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "برند"
        verbose_name_plural = "برندها"
        ordering = ["title"]

    def __str__(self):
        return self.title
