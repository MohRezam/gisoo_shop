from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from apps.shared.models.base import BaseModel
from core_gisoo_backend.storage_backends.locations import magazine_thumbnail_path


class MagazineCategory(BaseModel):
    name = models.CharField(
        _("name"),
        max_length=100,
    )
    slug = models.SlugField(
        _("slug"),
        max_length=120,
        unique=True,
    )

    class Meta:
        verbose_name = _("Magazine Category")
        verbose_name_plural = _("Magazine Categories")
        ordering = ("name",)

    def __str__(self):
        return self.name


class Magazine(BaseModel):
    category = models.ForeignKey(
        MagazineCategory,
        on_delete=models.PROTECT,
        related_name="magazines",
        verbose_name=_("category"),
    )

    title = models.CharField(
        _("title"),
        max_length=255,
    )

    slug = models.SlugField(
        _("slug"),
        max_length=300,
        unique=True,
    )

    short_description = models.TextField(
        _("short description"),
    )

    content = models.TextField(
        _("content"),
    )

    thumbnail = models.ImageField(
        _("thumbnail"),
        upload_to=magazine_thumbnail_path(),
    )

    published_at = models.DateTimeField(
        _("published at"),
    )

    is_published = models.BooleanField(
        _("is published"),
        default=False,
    )

    related_products = models.ManyToManyField(
        "products.Product",
        blank=True,
        related_name="related_magazines",
        verbose_name=_("related products"),
    )
    related_articles = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        related_name="related_to",
        verbose_name=_("related articles"),
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_("is_featured"),
    )

    reading_time = models.PositiveSmallIntegerField(
        verbose_name=_("reading_time"),
        help_text="زمان تقریبی مطالعه بر حسب دقیقه",
    )

    class Meta:
        verbose_name = _("Magazine")
        verbose_name_plural = _("Magazines")
        ordering = ("-published_at",)
        constraints = [
            models.UniqueConstraint(
                fields=["is_featured"],
                condition=Q(is_featured=True),
                name="unique_featured_magazine",
            ),
        ]

    def clean(self):
        super().clean()

        if self.is_featured:
            exists = Magazine.objects.filter(
                is_featured=True
            ).exclude(
                pk=self.pk
            ).exists()

            if exists:
                raise ValidationError({
                    "is_featured": (
                        "مقاله ویژه دیگری از قبل وجود دارد. "
                        "لطفاً ابتدا مقاله ویژه فعلی را غیرفعال کنید."
                    )
                })

    def __str__(self):
        return self.title
