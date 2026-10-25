from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0014_add_courier_carrier"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="customer_first_name",
            field=models.CharField(
                blank=True,
                default="",
                max_length=100,
                verbose_name="نام",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="customer_last_name",
            field=models.CharField(
                blank=True,
                default="",
                max_length=100,
                verbose_name="نام خانوادگی",
            ),
        ),
    ]
