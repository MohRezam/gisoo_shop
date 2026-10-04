from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shipping", "0004_add_shipping_carrier"),
    ]

    operations = [
        migrations.AddField(
            model_name="shippingmethod",
            name="estimated_days_min",
            field=models.PositiveSmallIntegerField(
                default=3,
                help_text="شروع بازه تحویل (مثلاً ۳ در «۳ تا ۵ روز»).",
                verbose_name="حداقل روز تخمینی",
            ),
        ),
        migrations.AlterField(
            model_name="shippingmethod",
            name="estimated_days",
            field=models.PositiveSmallIntegerField(
                default=5,
                help_text="پایان بازه تحویل و زمان پیامک تأیید تحویل (مثلاً ۵).",
                verbose_name="حداکثر روز تخمینی",
            ),
        ),
    ]
