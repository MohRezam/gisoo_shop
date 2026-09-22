from django.db import models

from apps.shared.models.base import BaseModel


class InAppNotificationType(models.TextChoices):
    ORDER = "order", "سفارش"
    OFFER = "offer", "پیشنهاد"
    STOCK = "stock", "موجودی"
    SYSTEM = "system", "سیستم"


class InAppNotification(BaseModel):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="in_app_notifications",
        verbose_name="کاربر",
    )
    title = models.CharField(max_length=255, verbose_name="عنوان")
    body = models.TextField(verbose_name="متن")
    type = models.CharField(
        max_length=32,
        choices=InAppNotificationType.choices,
        default=InAppNotificationType.SYSTEM,
        db_index=True,
        verbose_name="نوع",
    )
    link = models.CharField(
        max_length=512,
        blank=True,
        null=True,
        verbose_name="لینک",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="in_app_notifications",
        verbose_name="سفارش",
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="مهلت اقدام",
        help_text="اگر تنظیم شود، در اینباکس کاربر شمارندهٔ معکوس نشان داده می‌شود.",
    )
    is_read = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="خوانده‌شده",
    )

    class Meta:
        verbose_name = "اعلان درون‌برنامه‌ای"
        verbose_name_plural = "اعلان‌های درون‌برنامه‌ای"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} → {self.user_id}"
