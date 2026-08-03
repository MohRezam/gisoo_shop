from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.shared.models.base import BaseModel


class DiscountType(models.TextChoices):
    PERCENTAGE = "percentage", _("Percentage")
    FIXED = "fixed", _("Fixed amount")


class Discount(BaseModel):
    code = models.CharField(
        verbose_name=_("Code"),
        max_length=50,
        unique=True,
    )

    discount_type = models.CharField(
        verbose_name=_("Discount type"),
        max_length=20,
        choices=DiscountType.choices,
    )

    value = models.PositiveBigIntegerField(
        verbose_name=_("Value"),
        default=0,
    )

    minimum_order_amount = models.PositiveBigIntegerField(
        verbose_name=_("Minimum order amount"),
        default=0,
    )

    maximum_discount_amount = models.PositiveBigIntegerField(
        verbose_name=_("Maximum discount amount"),
        null=True,
        blank=True,
    )

    usage_limit = models.PositiveIntegerField(
        verbose_name=_("Usage limit"),
        default=0,
        help_text=_("0 means unlimited."),
    )

    used_count = models.PositiveIntegerField(
        verbose_name=_("Used count"),
        default=0,
    )

    per_user_limit = models.PositiveIntegerField(
        verbose_name=_("Per user limit"),
        default=1,
    )

    starts_at = models.DateTimeField(
        verbose_name=_("Starts at"),
    )

    expires_at = models.DateTimeField(
        verbose_name=_("Expires at"),
    )

    is_active = models.BooleanField(
        verbose_name=_("Is active"),
        default=True,
    )

    class Meta:
        verbose_name = _("Discount")
        verbose_name_plural = _("Discounts")
        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return self.code

    @property
    def is_valid(self):
        now = timezone.now()

        return (
            self.is_active
            and self.starts_at <= now <= self.expires_at
        )


class DiscountUsage(BaseModel):
    discount = models.ForeignKey(
        Discount,
        on_delete=models.CASCADE,
        related_name="usages",
        verbose_name=_("Discount"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="discount_usages",
        verbose_name=_("User"),
    )

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="discount_usages",
        verbose_name=_("Order"),
    )

    class Meta:
        verbose_name = _("Discount usage")
        verbose_name_plural = _("Discount usages")

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "discount",
                    "user",
                    "order",
                ],
                name="unique_discount_usage",
            )
        ]

    def __str__(self):
        return (
            f"{self.user} - "
            f"{self.discount.code}"
        )