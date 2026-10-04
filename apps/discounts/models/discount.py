from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.shared.models.base import BaseModel


class DiscountType(models.TextChoices):
    PERCENTAGE = "percentage", "درصدی"
    FIXED = "fixed", "مبلغ ثابت"


class Discount(BaseModel):
    code = models.CharField(
        verbose_name="کد",
        max_length=50,
        unique=True,
    )

    discount_type = models.CharField(
        verbose_name="نوع تخفیف",
        max_length=20,
        choices=DiscountType.choices,
    )

    value = models.PositiveBigIntegerField(
        verbose_name="مقدار",
        default=0,
        help_text=(
            "اگر نوع «درصدی» است عدد ۰ تا ۱۰۰ بگذارید "
            "(مثلاً ۱۰ یعنی ۱۰٪). "
            "اگر «مبلغ ثابت» است مبلغ به تومان "
            "(مثلاً ۳۰۰۰۰۰)."
        ),
    )

    minimum_order_amount = models.PositiveBigIntegerField(
        verbose_name="حداقل مبلغ سفارش",
        default=0,
    )

    maximum_discount_amount = models.PositiveBigIntegerField(
        verbose_name="حداکثر مبلغ تخفیف",
        null=True,
        blank=True,
    )

    applies_to_discounted_products = models.BooleanField(
        verbose_name="اعمال روی محصولات تخفیف‌دار",
        default=True,
        help_text=(
            "آیا این تخفیف روی محصولاتی که از قبل تخفیف محصول دارند "
            "هم قابل اعمال است."
        ),
    )

    usage_limit = models.PositiveIntegerField(
        verbose_name="سقف استفاده",
        default=0,
        help_text="۰ یعنی نامحدود.",
    )

    used_count = models.PositiveIntegerField(
        verbose_name="تعداد استفاده‌شده",
        default=0,
    )

    per_user_limit = models.PositiveIntegerField(
        verbose_name="سقف هر کاربر",
        default=1,
        help_text="۰ یعنی نامحدود.",
    )

    starts_at = models.DateTimeField(
        verbose_name="شروع",
    )

    expires_at = models.DateTimeField(
        verbose_name="انقضا",
    )

    is_active = models.BooleanField(
        verbose_name="فعال",
        default=True,
    )

    class Meta:
        verbose_name = "تخفیف"
        verbose_name_plural = "تخفیف‌ها"
        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return self.code

    def clean(self):
        super().clean()
        if (
            self.discount_type == DiscountType.PERCENTAGE
            and self.value > 100
        ):
            raise ValidationError(
                {
                    "value": (
                        "برای تخفیف درصدی، مقدار باید بین "
                        "۰ تا ۱۰۰ باشد. برای ۳۰۰ هزار تومان "
                        "نوع را «مبلغ ثابت» انتخاب کنید."
                    ),
                }
            )

    def save(self, *args, **kwargs):
        if self.code:
            self.code = self.code.strip().upper()
        self.full_clean()
        super().save(*args, **kwargs)

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
        verbose_name="تخفیف",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="discount_usages",
        verbose_name="کاربر",
    )

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="discount_usages",
        verbose_name="سفارش",
    )

    class Meta:
        verbose_name = "استفاده از تخفیف"
        verbose_name_plural = "استفاده‌های تخفیف"

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
