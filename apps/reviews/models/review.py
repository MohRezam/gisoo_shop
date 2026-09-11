from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.products.models import Product
from apps.shared.models.base import BaseModel
from django.core.exceptions import ValidationError


class ReviewStatus(models.TextChoices):
    PENDING = "pending", _("Pending")
    APPROVED = "approved", _("Approved")
    REJECTED = "rejected", _("Rejected")


class ProductReview(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="product_reviews",
        verbose_name=_("user"),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("product"),
    )

    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
        verbose_name=_("rating"),
    )

    comment = models.TextField(
        verbose_name=_("comment"),
    )

    status = models.CharField(
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING,
        verbose_name=_("status"),
    )

    is_featured = models.BooleanField(
        default=False,
        verbose_name=_("is featured"),
    )

    homepage_order = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("homepage order"),
    )

    class Meta:
        verbose_name = _("product review")
        verbose_name_plural = _("product reviews")
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_product_review",
            ),
            models.UniqueConstraint(
                fields=["homepage_order"],
                condition=models.Q(
                    is_featured=True,
                    homepage_order__isnull=False,
                ),
                name="unique_featured_homepage_order",
            ),
        ]

    def clean(self):
        if self.is_featured and self.homepage_order is None:
            raise ValidationError(
                {
                    "homepage_order": _(
                        "Featured reviews must have a homepage order."
                    )
                }
            )

    def __str__(self):
        return f"{self.user} - {self.product} - {self.rating}"
