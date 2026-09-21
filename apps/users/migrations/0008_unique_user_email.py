from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0007_unique_verified_phone_number"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="user",
            constraint=models.UniqueConstraint(
                condition=(
                    models.Q(("email__isnull", False))
                    & ~models.Q(("email", ""))
                ),
                fields=("email",),
                name="unique_user_email",
            ),
        ),
    ]
