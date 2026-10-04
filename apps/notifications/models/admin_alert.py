from django.db import models

from apps.shared.models.base import BaseModel


class AdminAlertType(models.TextChoices):
    RECEIPT = "receipt", "رسید پرداخت"
    ORDER = "order", "سفارش جدید"
    REVIEW = "review", "نظر جدید"
    CONSULTATION = "consultation", "درخواست مشاوره"
    SYSTEM = "system", "سیستم"


class AdminAlert(BaseModel):
    """In-admin notifications for shop staff / employer."""

    type = models.CharField(
        max_length=32,
        choices=AdminAlertType.choices,
        default=AdminAlertType.SYSTEM,
        db_index=True,
        verbose_name="نوع",
    )
    title = models.CharField(max_length=255, verbose_name="عنوان")
    body = models.TextField(blank=True, verbose_name="متن")
    link = models.CharField(
        max_length=512,
        blank=True,
        default="",
        verbose_name="لینک ادمین",
        help_text="مسیر نسبی داخل پنل ادمین، مثلاً /admin/payments/paymentintent/1/change/",
    )
    is_read = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="خوانده‌شده",
    )

    class Meta:
        verbose_name = "اعلان مدیریت"
        verbose_name_plural = "اعلان‌های مدیریت"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
