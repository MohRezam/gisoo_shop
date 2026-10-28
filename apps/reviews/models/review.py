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
        null=True,
        blank=True,
        verbose_name="کاربر",
    )
    author_name = models.CharField(
        max_length=80,
        blank=True,
        default="",
        verbose_name="نام نویسنده",
        help_text=(
            "برای نظر دستی این نام روی سایت دیده می‌شود و لازم نیست کاربر بسازید. "
            "اگر خالی باشد، نام یا شماره همان کاربر نشان داده می‌شود."
        ),
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
        errors = {}
        if self.is_featured and self.homepage_order is None:
            errors["homepage_order"] = "برای نظرات ویژه باید ترتیب صفحه اصلی مشخص شود."
        if not self.user_id and not (self.author_name or "").strip():
            errors["author_name"] = "برای نظر دستی نام نویسنده را بنویسید، یا یک کاربر انتخاب کنید."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.author_name = (self.author_name or "").strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{review_author_label(self)} - {self.product_id} - {self.rating}"


def review_author_label(review):
    written = (review.author_name or "").strip()
    if written:
        return written
    user = review.user
    if user is None:
        return "کاربر گیسو سنتر"
    full_name = " ".join(
        part for part in (user.first_name, user.last_name) if part
    ).strip()
    if full_name:
        return full_name
    phone = user.phone_number or ""
    if len(phone) <= 7:
        return "*" * len(phone)
    return phone[:4] + "*" * (len(phone) - 8) + phone[-4:]
