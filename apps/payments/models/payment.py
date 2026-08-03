from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shared.models.base import BaseModel


class PaymentStatus(models.TextChoices):
    PENDING = (
        "pending",
        _("Pending"),
    )

    PROCESSING = (
        "processing",
        _("Processing"),
    )

    SUCCESS = (
        "success",
        _("Success"),
    )

    FAILED = (
        "failed",
        _("Failed"),
    )

    CANCELED = (
        "canceled",
        _("Canceled"),
    )


class Payment(BaseModel):
    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.PROTECT,
        related_name="payment",
        verbose_name=_("order"),
    )

    amount = models.PositiveBigIntegerField(
        verbose_name=_("amount"),
    )

    status = models.CharField(
        max_length=32,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        verbose_name=_("status"),
    )

    gateway_payment_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("gateway payment id"),
    )

    gateway_reference_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("gateway reference id"),
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("paid at"),
    )

    class Meta:
        verbose_name = _("payment")
        verbose_name_plural = _("payments")

    def __str__(self):
        return f"Payment #{self.pk}"
