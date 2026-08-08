from django.core.exceptions import ValidationError

from apps.products.models import Product, ProductVariant
from apps.shared.models.base import BaseModel
from django.db import models
from django.utils.translation import gettext_lazy as _


class Bundle(BaseModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="bundles",
        verbose_name=_("product"),
    )

    title = models.CharField(
        max_length=255,
        verbose_name=_("title"),
    )

    description = models.TextField(
        blank=True,
        verbose_name=_("description"),
    )

    price = models.PositiveBigIntegerField(
        verbose_name=_("price"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("is_active"),
    )

    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("display_order"),
    )

    class Meta:
        verbose_name = _("bundle")
        verbose_name_plural = _("bundles")
        ordering = [
            "display_order",
            "-created_at",
        ]

    def __str__(self):
        return f"{self.product.title} - {self.title}"

    def clean(self):
        if self.price <= 0:
            raise ValidationError(
                _("Bundle price must be greater than zero.")
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class BundleItem(BaseModel):
    bundle = models.ForeignKey(
        Bundle,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("bundle"),
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name="bundle_items",
        verbose_name=_("variant"),
    )

    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name=_("quantity"),
    )

    class Meta:
        verbose_name = _("bundle item")
        verbose_name_plural = _("bundle items")

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "bundle",
                    "variant",
                ],
                name="unique_bundle_variant",
            )
        ]

    def __str__(self):
        return (
            f"{self.bundle.title} - "
            f"{self.variant.sku} × {self.quantity}"
        )

    def clean(self):
        if self.quantity < 1:
            raise ValidationError(
                _("Quantity must be greater than zero.")
            )

        if self.variant.product_id != self.bundle.product_id:
            raise ValidationError(
                _("Variant must belong to the selected product.")
            )

        if not self.variant.is_active:
            raise ValidationError(
                _("Variant must be active.")
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
