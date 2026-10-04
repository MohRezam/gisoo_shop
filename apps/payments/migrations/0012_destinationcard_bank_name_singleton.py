from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0011_persian_guide_video_labels"),
    ]

    operations = [
        migrations.AddField(
            model_name="destinationcard",
            name="bank_name",
            field=models.CharField(
                blank=True,
                default="",
                help_text="اختیاری — مثلاً ملت، سامان، ملی.",
                max_length=100,
                verbose_name="نام بانک",
            ),
        ),
        migrations.AlterField(
            model_name="destinationcard",
            name="card_number",
            field=models.CharField(
                help_text="۱۶ رقم شماره کارت مقصد (بدون فاصله).",
                max_length=16,
                unique=True,
                verbose_name="شماره کارت",
            ),
        ),
        migrations.AlterField(
            model_name="destinationcard",
            name="display_pan",
            field=models.CharField(
                blank=True,
                default="",
                max_length=32,
                verbose_name="شماره کارت (نمایشی)",
            ),
        ),
        migrations.AlterField(
            model_name="destinationcard",
            name="is_active",
            field=models.BooleanField(
                default=True,
                help_text="اگر خاموش باشد، صفحه پرداخت کارت مقصد ندارد.",
                verbose_name="فعال در فروشگاه",
            ),
        ),
        migrations.AlterField(
            model_name="destinationcard",
            name="masked_pan",
            field=models.CharField(
                blank=True,
                default="",
                max_length=32,
                verbose_name="شماره کارت (ماسک‌شده)",
            ),
        ),
        migrations.AlterField(
            model_name="destinationcard",
            name="name",
            field=models.CharField(
                help_text="نامی که روی کارت یا در صفحه پرداخت به مشتری نشان داده می‌شود.",
                max_length=100,
                verbose_name="نام دارنده",
            ),
        ),
        migrations.AlterModelOptions(
            name="destinationcard",
            options={
                "verbose_name": "کارت مقصد",
                "verbose_name_plural": "کارت مقصد",
            },
        ),
    ]
