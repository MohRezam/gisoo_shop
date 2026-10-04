# Generated manually for ShippingCarrier.COURIER (پیک) on Order

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0013_alter_orderstatushistory_source"),
        ("shipping", "0006_add_courier_carrier"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="carrier",
            field=models.CharField(
                blank=True,
                choices=[
                    ("post", "پست"),
                    ("tipax", "تیپاکس"),
                    ("courier", "پیک"),
                ],
                default="",
                max_length=16,
                verbose_name="حامل",
            ),
        ),
    ]
