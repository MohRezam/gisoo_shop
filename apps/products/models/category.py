from apps.shared.models.base import BaseModel
from django.db import models

from core_gisoo_backend.storage_backends.locations import category_image_path


class Category(BaseModel):
    title = models.CharField(
        max_length=255,
        verbose_name="عنوان",
    )

    slug = models.SlugField(
        unique=True,
        verbose_name="اسلاگ",
    )
    image = models.ImageField(
        upload_to=category_image_path(),
        verbose_name="تصویر",
        null=True,
        blank=True
    )
    short_description = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name="توضیحات کوتاه",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="children",
        verbose_name="والد",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش",
        help_text="عدد کوچک‌تر زودتر در صفحه اصلی نمایش داده می‌شود.",
    )

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ["display_order", "title"]

    def __str__(self):
        return self.title
