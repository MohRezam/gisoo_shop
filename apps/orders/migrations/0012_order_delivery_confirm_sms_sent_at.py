from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0011_order_payment_reminders"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="delivery_confirm_sms_sent_at",
            field=models.DateTimeField(
                blank=True,
                help_text="پیامک درخواست تأیید تحویل پس از پایان بازه تخمینی ارسال.",
                null=True,
                verbose_name="زمان پیامک تأیید تحویل",
            ),
        ),
    ]
