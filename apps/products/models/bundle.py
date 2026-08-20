from django.core.exceptions import ValidationError

from apps.products.models import Product, ProductVariant
from apps.shared.models.base import BaseModel
from django.db import models
from django.utils.translation import gettext_lazy as _


class Bundle(BaseModel):
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="bundles",
        verbose_name=_("variant"),
    )

    title = models.CharField(
        max_length=255,
        verbose_name=_("title"),
    )

    description = models.TextField(
        blank=True,
        verbose_name=_("description"),
    )

    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name=_("quantity"),
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
        return f"{self.variant.product.title} - {self.title}"

    def clean(self):
        super().clean()

        if self.quantity < 1:
            raise ValidationError(
                _("Bundle quantity must be greater than zero.")
            )

        if self.price <= 0:
            raise ValidationError(
                _("Bundle price must be greater than zero.")
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
