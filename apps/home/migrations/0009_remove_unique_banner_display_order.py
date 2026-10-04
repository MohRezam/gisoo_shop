from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0008_sync_model_state"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="banner",
            name="unique_banner_display_order",
        ),
    ]
