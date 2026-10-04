# Generated manually for ShippingCarrier.COURIER (پیک)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shipping", "0005_shippingmethod_estimated_days_min"),
    ]

    operations = [
        migrations.AlterField(
            model_name="shippingmethod",
            name="carrier",
            field=models.CharField(
                choices=[
                    ("post", "پست"),
                    ("tipax", "تیپاکس"),
                    ("courier", "پیک"),
                ],
                default="post",
                help_text=(
                    "پست و تیپاکس برای رهگیری آنلاین؛ "
                    "پیک برای ارسال محلی/موتوری بدون لینک رهگیری."
                ),
                max_length=16,
                verbose_name="حامل",
            ),
        ),
    ]
