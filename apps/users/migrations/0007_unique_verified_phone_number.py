# Generated manually for unique verified phone numbers

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0006_sync_model_state"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="userphonenumber",
            constraint=models.UniqueConstraint(
                condition=models.Q(is_verified=True),
                fields=("phone_number",),
                name="unique_verified_phone_number",
            ),
        ),
    ]
