from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shipping", "0002_sync_model_state"),
    ]

    operations = [
        migrations.AlterField(
            model_name="shippingmethod",
            name="free_shipping_minimum",
            field=models.PositiveBigIntegerField(
                default=0,
                help_text="۰ یعنی ارسال رایگان غیرفعال است.",
                verbose_name="حداقل ارسال رایگان",
            ),
        ),
    ]
