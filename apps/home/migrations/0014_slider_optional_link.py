from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0013_seed_contact_faqs"),
    ]

    operations = [
        migrations.AlterField(
            model_name="slider",
            name="link_type",
            field=models.CharField(
                choices=[
                    ("product", "محصول"),
                    ("category", "دسته‌بندی"),
                    ("none", "بدون لینک"),
                ],
                default="none",
                help_text=(
                    "اگر اسلایدر فقط نمایشی است، «بدون لینک» را انتخاب کنید."
                ),
                max_length=20,
                verbose_name="نوع لینک",
            ),
        ),
    ]
