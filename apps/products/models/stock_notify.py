from django.conf import settings
from django.db import models

from apps.products.models import Product
from apps.shared.models.base import BaseModel


class WishlistStockNotify(BaseModel):
    """User asked to be notified when a product is back in stock."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="stock_notify_requests",
        null=True,
        blank=True,
    )
    guest_token = models.UUIDField(null=True, blank=True, db_index=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="stock_notify_requests",
    )
    is_notified = models.BooleanField(default=False)
    notified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "اطلاع موجودی"
        verbose_name_plural = "اطلاع‌های موجودی"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                condition=models.Q(user__isnull=False),
                name="unique_user_product_stock_notify",
            ),
        ]

    def __str__(self):
        return f"Notify {self.product_id} → user={self.user_id}"
