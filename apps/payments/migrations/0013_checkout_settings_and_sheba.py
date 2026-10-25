from django.db import migrations, models

import apps.payments.models.checkout_settings as checkout_settings


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0012_destinationcard_bank_name_singleton"),
    ]

    operations = [
        migrations.AddField(
            model_name="destinationcard",
            name="sheba_number",
            field=models.CharField(
                blank=True,
                default="",
                help_text="۲۶ کاراکتر: IR و ۲۴ رقم. مثال IR800560014868100012345678. خالی یعنی شبا نشان داده نشود.",
                max_length=26,
                verbose_name="شماره شبا",
            ),
        ),
        migrations.AddField(
            model_name="destinationcard",
            name="sheba_min_amount",
            field=models.PositiveBigIntegerField(
                default=0,
                help_text=(
                    "اگر مبلغ سفارش به این عدد برسد، شماره شبا بالای کارت نشان داده می‌شود. "
                    "۰ یعنی شبا نمایش داده نشود."
                ),
                verbose_name="نمایش شبا از این مبلغ (تومان)",
            ),
        ),
        migrations.CreateModel(
            name="ShopCheckoutSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "min_order_amount",
                    models.PositiveBigIntegerField(
                        default=0,
                        help_text="۰ یعنی محدودیتی نیست.",
                        verbose_name="حداقل مبلغ خرید (تومان)",
                    ),
                ),
                (
                    "max_order_amount",
                    models.PositiveBigIntegerField(
                        default=0,
                        help_text="۰ یعنی محدودیتی نیست.",
                        verbose_name="حداکثر مبلغ خرید (تومان)",
                    ),
                ),
                (
                    "payment_expiration_minutes",
                    models.PositiveSmallIntegerField(
                        default=20,
                        help_text="فقط برای سفارش‌های جدید. پیش‌فرض ۲۰ دقیقه.",
                        verbose_name="مهلت کارت‌به‌کارت (دقیقه)",
                    ),
                ),
                (
                    "terms",
                    models.TextField(
                        blank=True,
                        default=checkout_settings.DEFAULT_PAYMENT_TERMS,
                        help_text="هر قانون را در یک خط بنویسید.",
                        verbose_name="قوانین صفحه کارت‌به‌کارت",
                    ),
                ),
                (
                    "support_url",
                    models.URLField(
                        blank=True,
                        default="",
                        help_text="اگر خالی باشد، همان لینک واتساپ سایت استفاده می‌شود.",
                        max_length=500,
                        verbose_name="لینک پشتیبانی صفحه پرداخت",
                    ),
                ),
            ],
            options={
                "verbose_name": "تنظیمات خرید و پرداخت",
                "verbose_name_plural": "تنظیمات خرید و پرداخت",
            },
        ),
    ]
