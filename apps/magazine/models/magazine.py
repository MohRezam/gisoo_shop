from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from apps.shared.models.base import BaseModel
from core_gisoo_backend.storage_backends.locations import magazine_thumbnail_path


class MagazineCategory(BaseModel):
    name = models.CharField(
        "نام",
        max_length=100,
    )
    slug = models.SlugField(
        "اسلاگ",
        max_length=120,
        unique=True,
    )

    class Meta:
        verbose_name = "دسته‌بندی مجله"
        verbose_name_plural = "دسته‌بندی‌های مجله"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Magazine(BaseModel):
    category = models.ForeignKey(
        MagazineCategory,
        on_delete=models.PROTECT,
        related_name="magazines",
        verbose_name="دسته‌بندی",
    )

    title = models.CharField(
        "عنوان",
        max_length=255,
    )

    slug = models.SlugField(
        "اسلاگ",
        max_length=300,
        unique=True,
    )

    short_description = models.TextField(
        "توضیح کوتاه",
    )

    content = models.TextField(
        "محتوا",
    )

    thumbnail = models.ImageField(
        "تصویر شاخص",
        upload_to=magazine_thumbnail_path(),
    )

    published_at = models.DateTimeField(
        "تاریخ انتشار",
    )

    is_published = models.BooleanField(
        "منتشر شده",
        default=False,
    )

    related_products = models.ManyToManyField(
        "products.Product",
        blank=True,
        related_name="related_magazines",
        verbose_name="محصولات مرتبط",
    )
    related_articles = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        related_name="related_to",
        verbose_name="مقالات مرتبط",
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name="مقاله ویژه",
    )

    reading_time = models.PositiveSmallIntegerField(
        verbose_name="زمان مطالعه (دقیقه)",
        help_text="زمان تقریبی مطالعه بر حسب دقیقه",
        default=3,
    )

    class Meta:
        verbose_name = "مجله"
        verbose_name_plural = "مجلات"
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
