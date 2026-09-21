from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("discounts", "0004_sync_model_state"),
    ]

    operations = [
        migrations.AlterField(
            model_name="discount",
            name="per_user_limit",
            field=models.PositiveIntegerField(
                default=1,
                help_text="۰ یعنی نامحدود.",
                verbose_name="سقف هر کاربر",
            ),
        ),
    ]
