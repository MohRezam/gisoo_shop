from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0015_extra_customer_sms_toggles"),
    ]

    operations = [
        migrations.AlterField(
            model_name="smssettings",
            name="sms_payment_success",
            field=models.BooleanField(
                default=True,
                help_text="پیامک تأیید پرداخت موفق برای مشتری",
                verbose_name="تأیید پرداخت",
            ),
        ),
        migrations.AlterField(
            model_name="smssettings",
            name="sms_payment_reminder",
            field=models.BooleanField(
                default=True,
                help_text="پیامک یادآوری مهلت پرداخت برای مشتری",
                verbose_name="یادآوری پرداخت",
            ),
        ),
        migrations.AlterField(
            model_name="smssettings",
            name="sms_order_shipped",
            field=models.BooleanField(
                default=True,
                help_text="پیامک ارسال شدن سفارش برای مشتری",
                verbose_name="ارسال سفارش",
            ),
        ),
        migrations.AlterField(
            model_name="smssettings",
            name="sms_order_cancelled",
            field=models.BooleanField(
                default=True,
                help_text="پیامک لغو سفارش برای مشتری",
                verbose_name="لغو سفارش",
            ),
        ),
        migrations.AlterField(
            model_name="smssettings",
            name="sms_delivery_confirm",
            field=models.BooleanField(
                default=True,
                help_text="پیامک درخواست تأیید تحویل برای مشتری",
                verbose_name="تأیید تحویل",
            ),
        ),
    ]
