from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0018_product_show_in_special_offer_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="productvariant",
            options={
                "ordering": ["display_order", "created_at"],
                "verbose_name": "تنوع محصول",
                "verbose_name_plural": "تنوع‌های محصول",
            },
        ),
        migrations.AddField(
            model_name="product",
            name="is_gisoo_recommended",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "اگر فعال باشد، این محصول در فیلتر «پیشنهادی گیسو سنتر» "
                    "بالای لیست فروشگاه نمایش داده می‌شود."
                ),
                verbose_name="پیشنهادی گیسو سنتر",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="recommended_order",
            field=models.PositiveIntegerField(
                default=0,
                help_text=(
                    "عدد کوچک‌تر = اولویت بالاتر بین محصولات پیشنهادی. "
                    "فقط وقتی «پیشنهادی گیسو سنتر» فعال است معنا دارد."
                ),
                verbose_name="ترتیب پیشنهادی",
            ),
        ),
        migrations.AlterField(
            model_name="productvariant",
            name="display_order",
            field=models.PositiveIntegerField(
                default=0,
                help_text="عدد کوچک‌تر = نمایش زودتر در صفحه محصول.",
                verbose_name="ترتیب نمایش",
            ),
        ),
    ]
