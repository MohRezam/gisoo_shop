# Generated manually for SmsSettings singleton

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0009_polish_inapp_admin_labels"),
    ]

    operations = [
        migrations.CreateModel(
            name="SmsSettings",
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
                    "sms_order_created",
                    models.BooleanField(
                        default=True,
                        help_text="پیامک ثبت سفارش برای مشتری",
                        verbose_name="ثبت سفارش",
                    ),
                ),
                (
                    "sms_payment_success",
                    models.BooleanField(
                        default=True,
                        help_text="پیامک تأیید پرداخت موفق",
                        verbose_name="تأیید پرداخت",
                    ),
                ),
                (
                    "sms_payment_reminder",
                    models.BooleanField(
                        default=True,
                        help_text="پیامک یادآوری مهلت پرداخت",
                        verbose_name="یادآوری پرداخت",
                    ),
                ),
                (
                    "sms_order_shipped",
                    models.BooleanField(
                        default=True,
                        help_text="پیامک ارسال شدن سفارش",
                        verbose_name="ارسال سفارش",
                    ),
                ),
                (
                    "sms_order_cancelled",
                    models.BooleanField(
                        default=True,
                        help_text="پیامک لغو سفارش",
                        verbose_name="لغو سفارش",
                    ),
                ),
                (
                    "sms_delivery_confirm",
                    models.BooleanField(
                        default=True,
                        help_text="پیامک درخواست تأیید تحویل",
                        verbose_name="تأیید تحویل",
                    ),
                ),
                (
                    "sms_new_consultation",
                    models.BooleanField(
                        default=True,
                        help_text="پیامک اطلاع‌رسانی مشاوره جدید",
                        verbose_name="درخواست مشاوره جدید",
                    ),
                ),
                (
                    "sms_new_comment",
                    models.BooleanField(
                        default=True,
                        help_text="پیامک اطلاع‌رسانی نظر جدید",
                        verbose_name="نظر جدید محصول",
                    ),
                ),
                (
                    "sms_new_image",
                    models.BooleanField(
                        default=True,
                        help_text="پیامک اطلاع‌رسانی تصویر جدید مشاوره",
                        verbose_name="تصویر جدید مشاوره",
                    ),
                ),
            ],
            options={
                "verbose_name": "تنظیمات پیامک",
                "verbose_name_plural": "تنظیمات پیامک",
            },
        ),
    ]
