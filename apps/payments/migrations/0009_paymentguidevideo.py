from django.db import migrations, models


def create_default_guide(apps, schema_editor):
    PaymentGuideVideo = apps.get_model("payments", "PaymentGuideVideo")
    PaymentGuideVideo.objects.get_or_create(
        pk=1,
        defaults={
            "title": "آموزش پرداخت آسان",
            "external_url": "",
            "is_active": True,
        },
    )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0008_remove_unused_payment_review_statuses"),
    ]

    operations = [
        migrations.CreateModel(
            name="PaymentGuideVideo",
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
                    "title",
                    models.CharField(
                        default="آموزش پرداخت آسان",
                        max_length=255,
                        verbose_name="title",
                    ),
                ),
                (
                    "video",
                    models.FileField(
                        blank=True,
                        help_text="Upload an mp4/webm/mov file, or leave empty and use external URL.",
                        upload_to="media/payments/guide",
                        verbose_name="video file",
                    ),
                ),
                (
                    "external_url",
                    models.URLField(
                        blank=True,
                        default="",
                        help_text="Optional. Used when no uploaded file is set (e.g. CDN / direct mp4 link).",
                        max_length=1000,
                        verbose_name="external video url",
                    ),
                ),
                (
                    "poster",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="media/payments/guide/posters",
                        verbose_name="poster image",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="is active"),
                ),
            ],
            options={
                "verbose_name": "ویدیوی آموزش پرداخت",
                "verbose_name_plural": "ویدیوی آموزش پرداخت",
            },
        ),
        migrations.RunPython(create_default_guide, noop_reverse),
    ]
