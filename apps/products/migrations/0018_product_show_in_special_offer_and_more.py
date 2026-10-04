from django.db import migrations, models


def forwards_migrate_campaign_products(apps, schema_editor):
    DiscountCampaign = apps.get_model("products", "DiscountCampaign")
    Product = apps.get_model("products", "Product")

    product_ids = set()
    for campaign in DiscountCampaign.objects.all():
        product_ids.update(
            campaign.products.values_list("id", flat=True)
        )

    if product_ids:
        Product.objects.filter(id__in=product_ids).update(
            show_in_special_offer=True,
        )


def backwards_migrate_campaign_products(apps, schema_editor):
    DiscountCampaign = apps.get_model("products", "DiscountCampaign")
    Product = apps.get_model("products", "Product")

    campaign = DiscountCampaign.objects.first()
    if campaign is None:
        return

    products = Product.objects.filter(show_in_special_offer=True)
    campaign.products.set(products)


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0017_sync_model_state"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="show_in_special_offer",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "فقط محصولاتی که حداقل یک واریانت با قیمت تخفیف‌خورده دارند "
                    "می‌توانند در پیشنهاد ویژه نمایش داده شوند."
                ),
                verbose_name="نمایش در پیشنهاد ویژه",
            ),
        ),
        migrations.RunPython(
            forwards_migrate_campaign_products,
            backwards_migrate_campaign_products,
        ),
        migrations.RemoveField(
            model_name="discountcampaign",
            name="products",
        ),
        migrations.AlterModelOptions(
            name="discountcampaign",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "کمپین تخفیف",
                "verbose_name_plural": "کمپین تخفیف",
            },
        ),
    ]
