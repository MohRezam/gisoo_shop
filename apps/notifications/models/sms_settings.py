from django.db import models

from apps.shared.models.base import SingletonModel


# pattern_key -> SmsSettings field name (otp stays always-on via SMS_ENABLED only)
SMS_TOGGLE_FIELDS: tuple[tuple[str, str, str], ...] = (
    ("order_created", "sms_order_created", "ثبت سفارش"),
    ("payment_success", "sms_payment_success", "تأیید پرداخت"),
    ("payment_reminder", "sms_payment_reminder", "یادآوری پرداخت"),
    ("order_shipped", "sms_order_shipped", "ارسال سفارش"),
    ("order_cancelled", "sms_order_cancelled", "لغو سفارش"),
    ("delivery_confirm", "sms_delivery_confirm", "تأیید تحویل"),
    ("new_consultation", "sms_new_consultation", "درخواست مشاوره جدید"),
    ("new_comment", "sms_new_comment", "نظر جدید محصول"),
    ("new_image", "sms_new_image", "تصویر جدید مشاوره"),
)

PATTERN_TO_FIELD = {pattern: field for pattern, field, _ in SMS_TOGGLE_FIELDS}


class SmsSettings(SingletonModel):
    """
    Per-event SMS switches for the admin notifications panel.
    Global kill-switch remains settings.SMS_ENABLED.
    """

    sms_order_created = models.BooleanField(
        default=True,
        verbose_name="ثبت سفارش",
        help_text="پیامک ثبت سفارش برای مشتری",
    )
    sms_payment_success = models.BooleanField(
        default=True,
        verbose_name="تأیید پرداخت",
        help_text="پیامک تأیید پرداخت موفق",
    )
    sms_payment_reminder = models.BooleanField(
        default=True,
        verbose_name="یادآوری پرداخت",
        help_text="پیامک یادآوری مهلت پرداخت",
    )
    sms_order_shipped = models.BooleanField(
        default=True,
        verbose_name="ارسال سفارش",
        help_text="پیامک ارسال شدن سفارش",
    )
    sms_order_cancelled = models.BooleanField(
        default=True,
        verbose_name="لغو سفارش",
        help_text="پیامک لغو سفارش",
    )
    sms_delivery_confirm = models.BooleanField(
        default=True,
        verbose_name="تأیید تحویل",
        help_text="پیامک درخواست تأیید تحویل",
    )
    sms_new_consultation = models.BooleanField(
        default=True,
        verbose_name="درخواست مشاوره جدید",
        help_text="پیامک اطلاع‌رسانی مشاوره جدید",
    )
    sms_new_comment = models.BooleanField(
        default=True,
        verbose_name="نظر جدید محصول",
        help_text="پیامک اطلاع‌رسانی نظر جدید",
    )
    sms_new_image = models.BooleanField(
        default=True,
        verbose_name="تصویر جدید مشاوره",
        help_text="پیامک اطلاع‌رسانی تصویر جدید مشاوره",
    )

    class Meta:
        verbose_name = "تنظیمات پیامک"
        verbose_name_plural = "تنظیمات پیامک"

    def __str__(self):
        return "تنظیمات پیامک"

    def is_pattern_enabled(self, pattern_key: str) -> bool:
        field = PATTERN_TO_FIELD.get(pattern_key)
        if not field:
            return True
        return bool(getattr(self, field, True))


def is_sms_pattern_enabled(pattern_key: str) -> bool:
    """otp_login and unknown keys default to enabled (only SMS_ENABLED gates them)."""
    if pattern_key not in PATTERN_TO_FIELD:
        return True
    try:
        return SmsSettings.load().is_pattern_enabled(pattern_key)
    except Exception:
        return True
