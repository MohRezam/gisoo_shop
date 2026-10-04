from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0024_discountcampaign_persian_labels"),
    ]

    operations = [
        migrations.AlterField(
            model_name="productimage",
            name="is_primary",
            field=models.BooleanField(
                default=False,
                help_text="دقیقاً یک تصویر از هر محصول باید اصلی باشد.",
                verbose_name="تصویر اصلی",
            ),
        ),
    ]
