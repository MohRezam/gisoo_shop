from django.db import models

from apps.shared.models.base import BaseModel


class PaymentDestinationCard(BaseModel):
    """Active destination card for card-to-card (C2C) transfers."""

    card_number = models.CharField(
        max_length=19,
        verbose_name="شماره کارت",
    )
    bank_name = models.CharField(
        max_length=100,
        verbose_name="نام بانک",
    )
    holder_name = models.CharField(
        max_length=150,
        verbose_name="نام دارنده",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    class Meta:
        verbose_name = "کارت مقصد پرداخت"
        verbose_name_plural = "کارت‌های مقصد پرداخت"
        ordering = ["-is_active", "-id"]

    def __str__(self):
        return f"{self.holder_name} — {self.card_number}"
