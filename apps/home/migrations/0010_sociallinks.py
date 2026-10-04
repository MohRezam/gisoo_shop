from django.db import migrations, models


def create_default_social_links(apps, schema_editor):
    SocialLinks = apps.get_model("home", "SocialLinks")
    SocialLinks.objects.get_or_create(
        pk=1,
        defaults={
            "telegram_url": "https://t.me/",
            "instagram_url": "https://www.instagram.com/",
            "whatsapp_url": "https://wa.me/989004553585",
            "bale_url": "https://ble.ir/",
        },
    )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0009_remove_unique_banner_display_order"),
    ]

    operations = [
        migrations.CreateModel(
            name="SocialLinks",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "telegram_url",
                    models.URLField(
                        blank=True,
                        default="",
                        max_length=500,
                        verbose_name="telegram url",
                    ),
                ),
                (
                    "instagram_url",
                    models.URLField(
                        blank=True,
                        default="",
                        max_length=500,
                        verbose_name="instagram url",
                    ),
                ),
                (
                    "whatsapp_url",
                    models.URLField(
                        blank=True,
                        default="",
                        max_length=500,
                        verbose_name="whatsapp url",
                    ),
                ),
                (
                    "bale_url",
                    models.URLField(
                        blank=True,
                        default="",
                        max_length=500,
                        verbose_name="bale url",
                    ),
                ),
            ],
            options={
                "verbose_name": "لینک‌های شبکه‌های اجتماعی",
                "verbose_name_plural": "لینک‌های شبکه‌های اجتماعی",
            },
        ),
        migrations.RunPython(create_default_social_links, noop_reverse),
    ]
