from apps.shared.models.base import BaseModel
from django.db import models

from core_gisoo_backend.storage_backends.locations import hair_problem_image_path, hair_type_image_path


class HairProblem(BaseModel):
    title = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="عنوان",
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        verbose_name="اسلاگ",
    )

    image = models.ImageField(
        upload_to=hair_problem_image_path(),
        verbose_name="تصویر",
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    class Meta:
        verbose_name = "مشکل مو"
        verbose_name_plural = "مشکلات مو"
        ordering = ["title"]

    def __str__(self):
        return self.title


class HairType(BaseModel):
    title = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="عنوان",
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        verbose_name="اسلاگ",
    )

    image = models.ImageField(
        upload_to=hair_type_image_path(),
        verbose_name="تصویر",
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    class Meta:
        verbose_name = "نوع مو"
        verbose_name_plural = "انواع مو"
        ordering = ["title"]

    def __str__(self):
        return self.title
