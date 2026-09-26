from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0011_remove_smssettings_sms_new_image"),
    ]

    operations = [
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
                ],
                max_length=50,
            ),
        ),
    ]
