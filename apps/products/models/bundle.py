from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.products.models import ProductVariant
from apps.shared.models.base import BaseModel


class Bundle(BaseModel):
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="bundles",
        verbose_name="تنوع محصول",
    )

    title = models.CharField(
        max_length=255,
        verbose_name="عنوان",
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )

    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="تعداد",
    )

    price = models.PositiveBigIntegerField(
        verbose_name="قیمت",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش",
    )

    class Meta:
        verbose_name = "بسته"
        verbose_name_plural = "بسته‌ها"
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
