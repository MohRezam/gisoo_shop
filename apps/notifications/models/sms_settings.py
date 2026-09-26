from django.db import models

from apps.shared.models.base import SingletonModel


# pattern_key -> SmsSettings field name (otp stays always-on via SMS_ENABLED only)
# Customer-only events — no employer/staff SMS patterns.
SMS_TOGGLE_FIELDS: tuple[tuple[str, str, str], ...] = (
    ("order_created", "sms_order_created", "ثبت سفارش"),
    ("payment_success", "sms_payment_success", "تأیید پرداخت"),
    ("payment_reminder", "sms_payment_reminder", "یادآوری پرداخت"),
    ("payment_rejected", "sms_payment_rejected", "رد رسید پرداخت"),
    ("order_preparing", "sms_order_preparing", "آماده‌سازی سفارش"),
    ("order_shipped", "sms_order_shipped", "ارسال سفارش"),
    ("order_cancelled", "sms_order_cancelled", "لغو سفارش"),
    ("order_expired", "sms_order_expired", "انقضای سفارش"),
    ("delivery_confirm", "sms_delivery_confirm", "تأیید تحویل"),
    ("consultation_received", "sms_consultation_received", "ثبت درخواست مشاوره"),
    ("consultation_answered", "sms_consultation_answered", "پاسخ مشاوره"),
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
        help_text="پیامک تأیید پرداخت موفق برای مشتری",
    )
    sms_payment_reminder = models.BooleanField(
        default=True,
        verbose_name="یادآوری پرداخت",
        help_text="پیامک یادآوری مهلت پرداخت برای مشتری",
    )
    sms_payment_rejected = models.BooleanField(
        default=True,
        verbose_name="رد رسید پرداخت",
        help_text="پیامک رد شدن رسید پرداخت برای مشتری",
    )
    sms_order_preparing = models.BooleanField(
        default=True,
        verbose_name="آماده‌سازی سفارش",
        help_text="پیامک شروع آماده‌سازی سفارش برای مشتری",
    )
    sms_order_shipped = models.BooleanField(
        default=True,
        verbose_name="ارسال سفارش",
        help_text="پیامک ارسال شدن سفارش برای مشتری",
    )
    sms_order_cancelled = models.BooleanField(
        default=True,
        verbose_name="لغو سفارش",
        help_text="پیامک لغو سفارش برای مشتری",
    )
    sms_order_expired = models.BooleanField(
        default=True,
        verbose_name="انقضای سفارش",
        help_text="پیامک منقضی شدن مهلت پرداخت برای مشتری",
    )
    sms_delivery_confirm = models.BooleanField(
        default=True,
        verbose_name="تأیید تحویل",
        help_text="پیامک درخواست تأیید تحویل برای مشتری",
    )
    sms_consultation_received = models.BooleanField(
        default=True,
        verbose_name="ثبت درخواست مشاوره",
        help_text="پیامک تأیید ثبت درخواست مشاوره برای مشتری",
    )
    sms_consultation_answered = models.BooleanField(
        default=True,
        verbose_name="پاسخ مشاوره",
        help_text="پیامک آماده بودن پاسخ مشاوره برای مشتری",
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
