from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.products.models import Product
from apps.shared.models.base import BaseModel


class ReviewStatus(models.TextChoices):
    PENDING = "pending", "در انتظار بررسی"
    APPROVED = "approved", "تأیید شده"
    REJECTED = "rejected", "رد شده"


class ProductReview(BaseModel):
    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        verbose_name="تاریخ ایجاد",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        null=True,
        verbose_name="آخرین به‌روزرسانی",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="product_reviews",
        verbose_name="کاربر",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="محصول",
    )

    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
        verbose_name="امتیاز",
    )

    comment = models.TextField(
        verbose_name="متن نظر",
    )

    status = models.CharField(
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING,
        verbose_name="وضعیت",
    )

    is_featured = models.BooleanField(
        default=False,
        verbose_name="ویژه صفحه اصلی",
    )

    homepage_order = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="ترتیب در صفحه اصلی",
    )

    class Meta:
        verbose_name = "نظر محصول"
        verbose_name_plural = "نظرات محصول"
        ordering = ["-created_at"]

        constraints = [
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
                    "homepage_order": (
                        "برای نظرات ویژه باید ترتیب صفحه اصلی مشخص شود."
                    )
                }
            )

    def __str__(self):
        return f"{self.user} - {self.product} - {self.rating}"
