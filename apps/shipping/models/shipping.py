from django.db import models
from django.utils.translation import (
    gettext_lazy as _,
)

from apps.shared.models.base import BaseModel


class ShippingMethod(BaseModel):
    title = models.CharField(
        verbose_name=_("Title"),
        max_length=255,
        unique=True,
    )

    price = models.PositiveBigIntegerField(
        verbose_name=_("Price"),
        default=0
    )

    free_shipping_minimum = models.PositiveBigIntegerField(
        verbose_name=_("Free shipping minimum"),
        default=0,
    )

    estimated_days = models.PositiveSmallIntegerField(
        verbose_name=_("Estimated days"),
        default=3,
    )

    is_active = models.BooleanField(
        verbose_name=_("Is active"),
        default=True,
    )

    class Meta:
        verbose_name = _("Shipping Method")
        verbose_name_plural = _(
            "Shipping Methods"
        )
        ordering = [
            "price",
        ]

    def __str__(
            self,
    ):
        return self.title


class ShipmentStatus(
    models.TextChoices,
):
    PENDING = (
        "pending",
        _("Pending"),
    )

    SHIPPED = (
        "shipped",
        _("Shipped"),
    )

    DELIVERED = (
        "delivered",
        _("Delivered"),
    )

    RETURNED = (
        "returned",
        _("Returned"),
    )


from django.conf import settings


class Shipment(BaseModel):
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="shipments",
    )

    status = models.CharField(
        max_length=20,
        choices=ShipmentStatus.choices,
        default=ShipmentStatus.PENDING,
    )

    tracking_code = models.CharField(
        max_length=255,
        blank=True,
    )

    shipped_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_shipments",
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

    def __str__(
            self,
    ):
        return (
            f"Shipment #{self.pk}"
        )
