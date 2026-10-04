from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0006_orderitem_original_unit_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="public_number",
            field=models.CharField(
                blank=True,
                db_index=True,
                max_length=32,
                null=True,
                unique=True,
                verbose_name="شماره عمومی",
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("created", "ایجاد شده"),
                    ("waiting_payment", "در انتظار پرداخت"),
                    ("payment_rejected", "پرداخت رد شده"),
                    ("preparing", "در حال آماده‌سازی"),
                    ("shipped", "ارسال شده"),
                    ("delivered", "تحویل شده"),
                    ("canceled", "لغو شده"),
                    ("expired", "منقضی شده"),
                ],
                default="waiting_payment",
                max_length=30,
                verbose_name="وضعیت",
            ),
        ),
        migrations.AlterField(
            model_name="orderstatushistory",
            name="new_status",
            field=models.CharField(
                choices=[
                    ("created", "ایجاد شده"),
                    ("waiting_payment", "در انتظار پرداخت"),
                    ("payment_rejected", "پرداخت رد شده"),
                    ("preparing", "در حال آماده‌سازی"),
                    ("shipped", "ارسال شده"),
                    ("delivered", "تحویل شده"),
                    ("canceled", "لغو شده"),
                    ("expired", "منقضی شده"),
                ],
                max_length=30,
            ),
        ),
        migrations.AlterField(
            model_name="orderstatushistory",
            name="old_status",
            field=models.CharField(
                choices=[
                    ("created", "ایجاد شده"),
                    ("waiting_payment", "در انتظار پرداخت"),
                    ("payment_rejected", "پرداخت رد شده"),
                    ("preparing", "در حال آماده‌سازی"),
                    ("shipped", "ارسال شده"),
                    ("delivered", "تحویل شده"),
                    ("canceled", "لغو شده"),
                    ("expired", "منقضی شده"),
                ],
                max_length=30,
            ),
        ),
    ]
