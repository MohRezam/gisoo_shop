from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0010_add_shipping_carrier"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="payment_reminder_sent_at",
            field=models.DateTimeField(
                blank=True,
                help_text="اولین یادآوری SMS/اعلان برای سفارش نیمه‌کاره.",
                null=True,
                verbose_name="زمان ارسال یادآوری پرداخت",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="payment_reminder_mid_sent_at",
            field=models.DateTimeField(
                blank=True,
                help_text="یادآوری دوم نزدیک به نیمهٔ مهلت پرداخت.",
                null=True,
                verbose_name="زمان یادآوری میانی پرداخت",
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="expires_at",
            field=models.DateTimeField(
                blank=True,
                help_text="مهلت پرداخت سفارش؛ بعد از این زمان سفارش منقضی می‌شود.",
                null=True,
                verbose_name="تاریخ انقضا",
            ),
        ),
    ]
