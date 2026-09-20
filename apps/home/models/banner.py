from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shared.models.base import BaseModel
from core_gisoo_backend.storage_backends.locations import banner_image_path, slider_image_path


class Banner(BaseModel):
    class LinkType(models.TextChoices):
        PRODUCT = "product", "محصول"
        CATEGORY = "category", "دسته‌بندی"
        CUSTOM = "custom", "لینک سفارشی"
        NONE = "none", "بدون لینک"

    image = models.ImageField(
        upload_to=banner_image_path(),
        verbose_name="تصویر",
    )

    link_type = models.CharField(
        max_length=20,
        choices=LinkType.choices,
        verbose_name="نوع لینک",
    )

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="banners",
        verbose_name="محصول",
    )

    category = models.ForeignKey(
        "products.Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="banners",
        verbose_name="دسته‌بندی",
    )

    custom_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name="لینک سفارشی",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    class Meta:
        verbose_name = "بنر"
        verbose_name_plural = "بنرها"
        ordering = ["display_order", "-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["display_order"],
                name="unique_banner_display_order",
            ),
        ]

    def __str__(self):
        return self.link_type

    def clean(self):
        super().clean()

        if self.link_type == self.LinkType.PRODUCT and not self.product:
            raise ValidationError({
                "product": "برای لینک محصول، انتخاب محصول الزامی است."
            })

        if self.link_type == self.LinkType.CATEGORY and not self.category:
            raise ValidationError({
                "category": "برای لینک دسته، انتخاب دسته‌بندی الزامی است."
            })

        if self.link_type == self.LinkType.CUSTOM and not self.custom_url:
            raise ValidationError({
                "custom_url": "برای لینک سفارشی، آدرس الزامی است."
            })

        if self.link_type != self.LinkType.PRODUCT:
            self.product = None

        if self.link_type != self.LinkType.CATEGORY:
            self.category = None

        if self.link_type != self.LinkType.CUSTOM:
            self.custom_url = ""


class Slider(BaseModel):
    class LinkType(models.TextChoices):
        PRODUCT = "product", "محصول"
        CATEGORY = "category", "دسته‌بندی"

    image = models.ImageField(
        upload_to=slider_image_path(),
        verbose_name="تصویر",
    )

    link_type = models.CharField(
        max_length=20,
        choices=LinkType.choices,
        verbose_name="نوع لینک",
    )

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sliders",
        verbose_name="محصول",
    )

    category = models.ForeignKey(
        "products.Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sliders",
        verbose_name="دسته‌بندی",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    class Meta:
        verbose_name = "اسلایدر"
        verbose_name_plural = "اسلایدرها"
        ordering = ["display_order", "-created_at"]

    def clean(self):
        super().clean()

        if self.link_type == self.LinkType.PRODUCT and not self.product:
            raise ValidationError({
                "product": "برای لینک محصول، انتخاب محصول الزامی است."
            })

        if self.link_type == self.LinkType.CATEGORY and not self.category:
            raise ValidationError({
                "category": "برای لینک دسته، انتخاب دسته‌بندی الزامی است."
            })

        if self.link_type != self.LinkType.PRODUCT:
            self.product = None

        if self.link_type != self.LinkType.CATEGORY:
            self.category = None

    def __str__(self):
        return str(self.image)
