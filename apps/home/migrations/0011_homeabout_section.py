from django.db import migrations, models


SECTION_KEYS = ("intro", "story", "cta")

STORY_TITLE = "چرا گیسو سنتر متولد شد؟"
STORY_DESCRIPTION = (
    "بسیاری از فروشگاه‌های عمومی، انتخاب محصول مراقبت مو را به حدس و تجربه پراکنده "
    "واگذار می‌کنند؛ در حالی که ریزش، کم‌پشتی یا آسیب مو نیاز به مسیر دقیق‌تری دارد.\n\n"
    "گیسو سنتر برای پر کردن همین فاصله شکل گرفت: تمرکز روی تخصص مو، اصالت کالا، و "
    "مشاوره واقعی قبل و بعد از خرید.\n\n"
    "هدف ما این است که هر محصول وارد فروشگاه، از فیلتر بررسی گذشته باشد و کاربر با "
    "اطمینان بیشتری انتخاب کند."
)

CTA_TITLE = "برای انتخاب محصول مطمئن نیستی؟"
CTA_DESCRIPTION = (
    "اگر هنوز نمی‌دانی کدام محصول برای نیاز موهایت مناسب است، تیم گیسو سنتر آماده "
    "راهنمایی توست."
)


def assign_sections(apps, schema_editor):
    HomeAbout = apps.get_model("home", "HomeAbout")
    rows = list(HomeAbout.objects.order_by("display_order", "-created_at", "id"))
    for index, row in enumerate(rows):
        if index < len(SECTION_KEYS):
            row.section = SECTION_KEYS[index]
        else:
            row.section = "intro"
        row.save(update_fields=["section"])

    # Ensure story / cta text rows exist even when only intro was seeded before.
    # Image is required: reuse intro image when available so admin can replace later.
    by_section = {
        row.section: row
        for row in HomeAbout.objects.order_by("display_order", "-created_at", "id")
    }
    intro = by_section.get("intro")
    image_name = intro.image.name if intro and intro.image else ""

    if "story" not in by_section and image_name:
        HomeAbout.objects.create(
            section="story",
            title=STORY_TITLE,
            description=STORY_DESCRIPTION,
            image=image_name,
            display_order=1,
            is_active=True,
        )
    if "cta" not in by_section and image_name:
        HomeAbout.objects.create(
            section="cta",
            title=CTA_TITLE,
            description=CTA_DESCRIPTION,
            image=image_name,
            display_order=2,
            is_active=True,
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0010_sociallinks"),
    ]

    operations = [
        migrations.AddField(
            model_name="homeabout",
            name="section",
            field=models.CharField(
                choices=[
                    ("intro", "معرفی (صفحه اصلی و درباره ما)"),
                    ("story", "داستان شکل‌گیری"),
                    ("cta", "دعوت به اقدام"),
                ],
                default="intro",
                help_text=(
                    "intro = homepage + about first block; "
                    "story / cta = about page second and third blocks."
                ),
                max_length=20,
                verbose_name="section",
            ),
        ),
        migrations.RunPython(assign_sections, noop_reverse),
    ]
