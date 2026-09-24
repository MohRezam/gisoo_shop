from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("reviews", "0003_sync_persian_labels"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="productreview",
            name="unique_user_product_review",
        ),
    ]
