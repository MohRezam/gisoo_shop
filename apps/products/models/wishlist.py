import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from apps.products.models import Product
from apps.shared.models.base import BaseModel


class Wishlist(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist",
        null=True,
        blank=True,
        verbose_name=_("user"),
    )

    guest_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        null=True,
        blank=True,
        editable=False,
        verbose_name=_("guest token"),
    )

    class Meta:
        verbose_name = _("wishlist")
        verbose_name_plural = _("wishlists")

        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(
                        user__isnull=False,
                        guest_token__isnull=True,
                    )
                    |
                    Q(
                        user__isnull=True,
                        guest_token__isnull=False,
                    )
                ),
                name="wishlist_owner_must_be_user_or_guest",
            )
        ]

    def __str__(self):
        if self.user_id:
            return f"Wishlist - {self.user}"

        return f"Guest Wishlist - {self.guest_token}"


class WishlistItem(BaseModel):
    wishlist = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("wishlist"),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="wishlist_items",
        verbose_name=_("product"),
    )

    class Meta:
        verbose_name = _("wishlist item")
        verbose_name_plural = _("wishlist items")

        constraints = [
            models.UniqueConstraint(
                fields=["wishlist", "product"],
                name="unique_wishlist_product",
            )
        ]

    def __str__(self):
        return f"{self.wishlist} - {self.product.title}"