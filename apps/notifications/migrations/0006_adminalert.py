import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0005_inappnotification_expires_at"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AdminAlert",
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
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                (
                    "archived",
                    models.BooleanField(default=False, verbose_name="archived"),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("receipt", "رسید پرداخت"),
                            ("order", "سفارش جدید"),
                            ("review", "نظر جدید"),
                            ("consultation", "درخواست مشاوره"),
                            ("system", "سیستم"),
                        ],
                        db_index=True,
                        default="system",
                        max_length=32,
                        verbose_name="نوع",
                    ),
                ),
                ("title", models.CharField(max_length=255, verbose_name="عنوان")),
                ("body", models.TextField(blank=True, verbose_name="متن")),
                (
                    "link",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text=(
                            "مسیر نسبی داخل پنل ادمین، مثلاً "
                            "/admin/payments/paymentintent/1/change/"
                        ),
                        max_length=512,
                        verbose_name="لینک ادمین",
                    ),
                ),
                (
                    "is_read",
                    models.BooleanField(
                        db_index=True, default=False, verbose_name="خوانده‌شده"
                    ),
                ),
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
            ],
            options={
                "verbose_name": "اعلان مدیریت",
                "verbose_name_plural": "اعلان‌های مدیریت",
                "ordering": ["-created_at"],
            },
        ),
    ]
