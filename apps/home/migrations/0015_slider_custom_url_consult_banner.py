from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0014_slider_optional_link"),
    ]

    operations = [
        migrations.AddField(
            model_name="slider",
            name="custom_url",
            field=models.URLField(
                blank=True,
                help_text=(
                    "برای لینک خارجی از https:// استفاده کنید؛ "
                    "در سایت در تب جدید باز می‌شود."
                ),
                max_length=500,
                verbose_name="لینک سفارشی",
            ),
        ),
        migrations.AlterField(
            model_name="slider",
            name="image",
            field=models.ImageField(
                help_text=(
                    "ابعاد پیشنهادی: ۱۹۲۰×۴۸۰ پیکسل (نسبت حدود ۴ به ۱). "
                    "محتوای مهم را وسط تصویر بگذارید تا روی موبایل بریده نشود."
                ),
                upload_to="media/home/slider",
                verbose_name="تصویر",
            ),
        ),
        migrations.AlterField(
            model_name="slider",
            name="link_type",
            field=models.CharField(
                choices=[
                    ("product", "محصول"),
                    ("category", "دسته‌بندی"),
                    ("custom", "لینک سفارشی / خارجی"),
                    ("none", "بدون لینک"),
                ],
                default="none",
                help_text=(
                    "محصول / دسته‌بندی / لینک سفارشی (مثلاً https://...) / بدون لینک."
                ),
                max_length=20,
                verbose_name="نوع لینک",
            ),
        ),
        migrations.AlterField(
            model_name="homeabout",
            name="section",
            field=models.CharField(
                choices=[
                    ("intro", "معرفی (صفحه اصلی و درباره ما)"),
                    ("story", "داستان شکل‌گیری"),
                    ("cta", "دعوت به اقدام"),
                    ("consult_banner", "بنر مشاوره صفحه اصلی"),
                ],
                default="intro",
                help_text=(
                    "intro = homepage + about first block; "
                    "story / cta = about page second and third blocks; "
                    "consult_banner = homepage consult banner above FAQs."
                ),
                max_length=20,
                verbose_name="section",
            ),
        ),
    ]
