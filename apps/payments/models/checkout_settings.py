from django.core.exceptions import ValidationError
from django.db import models

from apps.shared.models.base import SingletonModel


DEFAULT_PAYMENT_TERMS = (
    "تنها مبلغ و شماره کارت نمایش‌داده‌شده برای همین سفارش معتبر است.\n"
    "ثبت رسید به‌معنای تأیید پرداخت نیست؛ ورود واقعی وجه باید بررسی شود.\n"
    "با پایان مهلت، موجودی آزاد و اعتبار مبلغ یکتا متوقف می‌شود.\n"
    "در صورت پرداخت با کارت شخص دیگر یا مغایرت اطلاعات، سفارش وارد بررسی دستی می‌شود.\n"
    "پیامک ثبت نهایی فقط پس از تأیید واریز ارسال می‌شود.\n"
    "در صورت بازگشت وجه، پرداخت پس از بررسی فقط به مبدأ واریز بازگردانده می‌شود.\n"
    "فروشگاه رمز پویا، CVV2 یا تاریخ انقضای کارت مشتری را درخواست نمی‌کند."
)


class ShopCheckoutSettings(SingletonModel):
    """Singleton checkout limits and card-to-card page copy."""

    min_order_amount = models.PositiveBigIntegerField(
        default=0,
        verbose_name="حداقل مبلغ خرید (تومان)",
        help_text="۰ یعنی محدودیتی نیست.",
    )
    max_order_amount = models.PositiveBigIntegerField(
        default=0,
        verbose_name="حداکثر مبلغ خرید (تومان)",
        help_text="۰ یعنی محدودیتی نیست.",
    )
    payment_expiration_minutes = models.PositiveSmallIntegerField(
        default=20,
        verbose_name="مهلت کارت‌به‌کارت (دقیقه)",
        help_text="فقط برای سفارش‌های جدید. پیش‌فرض ۲۰ دقیقه.",
    )
    terms = models.TextField(
        blank=True,
        default=DEFAULT_PAYMENT_TERMS,
        verbose_name="قوانین صفحه کارت‌به‌کارت",
        help_text="هر قانون را در یک خط بنویسید.",
    )
    support_url = models.URLField(
        max_length=500,
        blank=True,
        default="",
        verbose_name="لینک پشتیبانی صفحه پرداخت",
        help_text="اگر خالی باشد، همان لینک واتساپ سایت استفاده می‌شود.",
    )

    class Meta:
        verbose_name = "تنظیمات خرید و پرداخت"
        verbose_name_plural = "تنظیمات خرید و پرداخت"

    def __str__(self):
        return "تنظیمات خرید و پرداخت"

    def clean(self):
        super().clean()
        if (
            self.min_order_amount
            and self.max_order_amount
            and self.max_order_amount < self.min_order_amount
        ):
            raise ValidationError(
                {"max_order_amount": "حداکثر خرید نمی‌تواند از حداقل کمتر باشد."}
            )
        if self.payment_expiration_minutes < 1:
            raise ValidationError(
                {"payment_expiration_minutes": "مهلت پرداخت باید حداقل ۱ دقیقه باشد."}
            )
