from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0013_remove_employer_sms_toggles"),
    ]

    operations = [
        migrations.AddField(
            model_name="smssettings",
            name="sms_consultation_answered",
            field=models.BooleanField(
                default=True,
                help_text="پیامک آماده بودن پاسخ مشاوره برای مشتری",
                verbose_name="پاسخ مشاوره",
            ),
        ),
        migrations.AlterField(
            model_name="notification",
            name="notification_type",
            field=models.CharField(
                choices=[
                    ("OTP", "OTP"),
                    ("ORDER_CREATED", "Order Created"),
                    ("PAYMENT_SUCCESS", "Payment Success"),
                    ("NEW_CONSULTATION", "New Consultation"),
                    ("NEW_COMMENT", "New Comment"),
                    ("ORDER_SHIPPED", "Order Shipped"),
                    ("ORDER_CANCELLED", "Order Cancelled"),
                    ("PAYMENT_REMINDER", "Payment Reminder"),
                    ("DELIVERY_CONFIRM", "Delivery Confirm"),
                    ("CONSULTATION_ANSWERED", "Consultation Answered"),
                ],
                max_length=50,
            ),
        ),
    ]
