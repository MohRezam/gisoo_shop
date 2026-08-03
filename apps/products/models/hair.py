from apps.shared.models.base import BaseModel
from django.db import models
from django.utils.translation import gettext_lazy as _

from core_gisoo_backend.storage_backends.locations import hair_problem_image_path, hair_type_image_path


class HairProblem(BaseModel):
    title = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("title"),
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        verbose_name=_("slug"),
    )

    image = models.ImageField(
        upload_to=hair_problem_image_path(),
        verbose_name=_("image"),
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("is_active"),
    )

    class Meta:
        verbose_name = _("Hair Problem")
        verbose_name_plural = _("Hair Problems")
        ordering = ["title"]

    def __str__(self):
        return self.title


class HairType(BaseModel):
    title = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("title"),
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        verbose_name=_("slug"),
    )

    image = models.ImageField(
        upload_to=hair_type_image_path(),
        verbose_name=_("image"),
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("is_active"),
    )

    class Meta:
        verbose_name = _("Hair Type")
        verbose_name_plural = _("Hair Types")
        ordering = ["title"]

    def __str__(self):
        return self.title
