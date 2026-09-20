# Generated manually for InAppNotification inbox feature

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0002_notification_idempotency_key"),
        ("orders", "0002_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="InAppNotification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                ("archived", models.BooleanField(default=False, verbose_name="archived")),
                ("title", models.CharField(max_length=255, verbose_name="عنوان")),
                ("body", models.TextField(verbose_name="متن")),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("order", "سفارش"),
                            ("offer", "پیشنهاد"),
                            ("stock", "موجودی"),
                            ("system", "سیستم"),
                        ],
                        db_index=True,
                        default="system",
                        max_length=32,
                        verbose_name="نوع",
                    ),
                ),
                ("link", models.CharField(blank=True, max_length=512, null=True, verbose_name="لینک")),
                ("is_read", models.BooleanField(db_index=True, default=False, verbose_name="خوانده‌شده")),
                (
                    "creator",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(app_label)s_%(class)s_creator",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="creator",
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="in_app_notifications",
                        to="orders.order",
                        verbose_name="سفارش",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="in_app_notifications",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="کاربر",
                    ),
                ),
            ],
            options={
                "verbose_name": "اعلان درون‌برنامه‌ای",
                "verbose_name_plural": "اعلان‌های درون‌برنامه‌ای",
                "ordering": ["-created_at"],
            },
        ),
    ]
