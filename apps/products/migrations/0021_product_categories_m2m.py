from django.db import migrations, models


def copy_category_to_m2m(apps, schema_editor):
    Product = apps.get_model("products", "Product")
    through = Product.categories.through
    rows = [
        through(product_id=product_id, category_id=category_id)
        for product_id, category_id in (
            Product.objects
            .filter(category_id__isnull=False)
            .values_list("id", "category_id")
        )
    ]
    if rows:
        through.objects.bulk_create(rows, ignore_conflicts=True)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0020_hairproblem_display_order"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="categories",
            field=models.ManyToManyField(
                blank=True,
                related_name="categorized_products",
                to="products.category",
                verbose_name="دسته‌بندی‌ها",
            ),
        ),
        migrations.RunPython(
            copy_category_to_m2m,
            noop_reverse,
        ),
        migrations.RemoveField(
            model_name="product",
            name="category",
        ),
        migrations.AlterField(
            model_name="product",
            name="categories",
            field=models.ManyToManyField(
                blank=True,
                related_name="products",
                to="products.category",
                verbose_name="دسته‌بندی‌ها",
            ),
        ),
    ]
