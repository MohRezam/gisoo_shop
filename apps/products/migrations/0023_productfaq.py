import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0022_polish_bundle_persian_labels"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductFAQ",
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
                    "question",
                    models.CharField(max_length=500, verbose_name="سوال"),
                ),
                (
                    "answer",
                    models.TextField(verbose_name="پاسخ"),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="فعال"),
                ),
                (
                    "ordering",
                    models.PositiveIntegerField(default=0, verbose_name="ترتیب"),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name="تاریخ ایجاد",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        verbose_name="تاریخ به‌روزرسانی",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="faqs",
                        to="products.product",
                        verbose_name="محصول",
                    ),
                ),
            ],
            options={
                "verbose_name": "سوال متداول محصول",
                "verbose_name_plural": "سوالات متداول محصول",
                "ordering": ["ordering", "id"],
            },
        ),
    ]
