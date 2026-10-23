from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0025_productimage_primary_label"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="display_order",
            field=models.PositiveIntegerField(
                default=0,
                help_text="عدد کوچک‌تر زودتر در صفحه اصلی نمایش داده می‌شود.",
                verbose_name="ترتیب نمایش",
            ),
        ),
        migrations.AlterModelOptions(
            name="category",
            options={
                "ordering": ["display_order", "title"],
                "verbose_name": "دسته‌بندی",
                "verbose_name_plural": "دسته‌بندی‌ها",
            },
        ),
    ]
