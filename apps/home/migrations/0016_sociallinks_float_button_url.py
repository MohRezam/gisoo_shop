from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0015_slider_custom_url_consult_banner"),
    ]

    operations = [
        migrations.AddField(
            model_name="sociallinks",
            name="float_button_url",
            field=models.URLField(
                blank=True,
                default="",
                help_text=(
                    "فقط دکمهٔ سبز گوشهٔ پایین سایت. "
                    "اگر خالی باشد همان لینک واتساپ استفاده می‌شود. "
                    "هر نشانی با http یا https مجاز است."
                ),
                max_length=500,
                verbose_name="لینک آیکون شناور",
            ),
        ),
    ]
