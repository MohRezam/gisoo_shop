from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shared.models.base import BaseModel
from core_gisoo_backend.storage_backends.locations import banner_image_path


class Banner(BaseModel):

    class LinkType(models.TextChoices):
        PRODUCT = "product", _("Product")
        CATEGORY = "category", _("Category")
        CUSTOM = "custom", _("Custom URL")
        NONE = "none", _("No link")

    title = models.CharField(
        max_length=255,
        verbose_name=_("title"),
    )

    image = models.ImageField(
        upload_to=banner_image_path(),
        verbose_name=_("image"),
    )

    link_type = models.CharField(
        max_length=20,
        choices=LinkType.choices,
        default=LinkType.NONE,
        verbose_name=_("link type"),
    )

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="banners",
        verbose_name=_("product"),
    )

    category = models.ForeignKey(
        "products.Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="banners",
        verbose_name=_("category"),
    )

    custom_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name=_("custom URL"),
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
        verbose_name = _("banner")
        verbose_name_plural = _("banners")
        ordering = ["display_order", "-created_at"]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()

        if self.link_type == self.LinkType.PRODUCT and not self.product:
            raise ValidationError({
                "product": _("Product is required for product link.")
            })

        if self.link_type == self.LinkType.CATEGORY and not self.category:
            raise ValidationError({
                "category": _("Category is required for category link.")
            })

        if self.link_type == self.LinkType.CUSTOM and not self.custom_url:
            raise ValidationError({
                "custom_url": _("Custom URL is required for custom link.")
            })

        if self.link_type != self.LinkType.PRODUCT:
            self.product = None

        if self.link_type != self.LinkType.CATEGORY:
            self.category = None

        if self.link_type != self.LinkType.CUSTOM:
            self.custom_url = ""