from django.conf import settings
from django.db import models


class UserPhoneNumber(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="phone_numbers",
        verbose_name="کاربر",
    )

    phone_number = models.CharField(
        "شماره تلفن",
        max_length=15,
    )

    is_verified = models.BooleanField(
        "تأییدشده",
        default=False,
    )

    is_primary = models.BooleanField(
        "اصلی",
        default=False,
    )

    created_at = models.DateTimeField(
        "تاریخ ایجاد",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        "تاریخ به‌روزرسانی",
        auto_now=True,
    )

    class Meta:
        verbose_name = "شماره تلفن کاربر"
        verbose_name_plural = "شماره‌های تلفن کاربر"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "phone_number"],
                name="unique_user_phone_number",
            ),
            models.UniqueConstraint(
                fields=["phone_number"],
                condition=models.Q(is_verified=True),
                name="unique_verified_phone_number",
            ),
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(is_primary=True),
                name="unique_primary_phone_per_user",
            ),
        ]
        ordering = ["-is_primary", "-created_at"]

    def __str__(self):
        return self.phone_number
