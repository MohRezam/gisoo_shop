from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0014_consultation_answered_sms"),
    ]

    operations = [
        migrations.AddField(
            model_name="smssettings",
            name="sms_payment_rejected",
            field=models.BooleanField(
                default=True,
                help_text="پیامک رد شدن رسید پرداخت برای مشتری",
                verbose_name="رد رسید پرداخت",
            ),
        ),
        migrations.AddField(
            model_name="smssettings",
            name="sms_order_preparing",
            field=models.BooleanField(
                default=True,
                help_text="پیامک شروع آماده‌سازی سفارش برای مشتری",
                verbose_name="آماده‌سازی سفارش",
            ),
        ),
        migrations.AddField(
            model_name="smssettings",
            name="sms_order_expired",
            field=models.BooleanField(
                default=True,
                help_text="پیامک منقضی شدن مهلت پرداخت برای مشتری",
                verbose_name="انقضای سفارش",
            ),
        ),
        migrations.AddField(
            model_name="smssettings",
            name="sms_consultation_received",
            field=models.BooleanField(
                default=True,
                help_text="پیامک تأیید ثبت درخواست مشاوره برای مشتری",
                verbose_name="ثبت درخواست مشاوره",
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
                    ("ORDER_PREPARING", "Order Preparing"),
                    ("ORDER_EXPIRED", "Order Expired"),
                    ("PAYMENT_REJECTED", "Payment Rejected"),
                    ("CONSULTATION_RECEIVED", "Consultation Received"),
                ],
                max_length=50,
            ),
        ),
    ]
