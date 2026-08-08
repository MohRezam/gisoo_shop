from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.products.models import ProductVariant
from apps.shared.models.base import BaseModel
from apps.users.models import User

import uuid
from django.core.exceptions import ValidationError


class Cart(BaseModel):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="carts",
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        verbose_name = _("cart")
        verbose_name_plural = _("carts")


class CartItem(BaseModel):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("cart"),
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name=_("variant"),
        null=True,
        blank=True,
    )

    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name=_("quantity"),
    )
    bundle = models.ForeignKey(
        "products.Bundle",
        on_delete=models.CASCADE,
        related_name="cart_items",
        null=True,
        blank=True,
        verbose_name=_("bundle"),
    )

    class Meta:
        verbose_name = _("cart item")
        verbose_name_plural = _("cart items")

        constraints = [
            models.UniqueConstraint(
                fields=["cart", "variant"],
                condition=models.Q(bundle__isnull=True),
                name="unique_cart_variant",
            ),
            models.UniqueConstraint(
                fields=["cart", "bundle"],
                condition=models.Q(variant__isnull=True),
                name="unique_cart_bundle",
            ),
        ]

    def clean(self):
        has_variant = self.variant is not None
        has_bundle = self.bundle is not None

        if has_variant == has_bundle:
            raise ValidationError(
                _("Select either a variant or a bundle.")
            )
        if has_bundle:
            if not self.bundle.is_active:
                raise ValidationError(
                    _("Selected bundle is not active.")
                )
        if self.quantity < 1:
            raise ValidationError(
                _("Quantity must be greater than zero.")
            )
