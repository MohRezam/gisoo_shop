from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0019_product_gisoo_recommended"),
    ]

    operations = [
        migrations.AddField(
            model_name="hairproblem",
            name="display_order",
            field=models.PositiveIntegerField(
                default=0,
                verbose_name="ترتیب نمایش",
            ),
        ),
        migrations.AlterModelOptions(
            name="hairproblem",
            options={
                "ordering": ["display_order", "title"],
                "verbose_name": "مشکل مو",
                "verbose_name_plural": "مشکلات مو",
            },
        ),
    ]
