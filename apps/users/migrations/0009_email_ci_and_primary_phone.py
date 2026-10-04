from django.db import migrations, models
from django.db.models import Count
from django.db.models.functions import Lower


def lowercase_emails_and_resolve_duplicates(apps, schema_editor):
    User = apps.get_model("users", "User")

    for user in User.objects.exclude(email__isnull=True).exclude(email=""):
        normalized = user.email.strip().lower()
        if user.email != normalized:
            user.email = normalized
            user.save(update_fields=["email"])

    duplicates = (
        User.objects.exclude(email__isnull=True)
        .exclude(email="")
        .values("email")
        .annotate(c=Count("id"))
        .filter(c__gt=1)
    )

    for row in duplicates:
        users = list(
            User.objects.filter(email=row["email"]).order_by("id")
        )
        for user in users[1:]:
            user.email = None
            user.save(update_fields=["email"])


def ensure_single_primary_phone(apps, schema_editor):
    UserPhoneNumber = apps.get_model("users", "UserPhoneNumber")
    user_ids = (
        UserPhoneNumber.objects.filter(is_primary=True)
        .values("user_id")
        .annotate(c=Count("id"))
        .filter(c__gt=1)
        .values_list("user_id", flat=True)
    )

    for user_id in user_ids:
        phones = list(
            UserPhoneNumber.objects.filter(
                user_id=user_id,
                is_primary=True,
            ).order_by("id")
        )
        for phone in phones[1:]:
            phone.is_primary = False
            phone.save(update_fields=["is_primary"])


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0008_unique_user_email"),
    ]

    operations = [
        migrations.RunPython(
            lowercase_emails_and_resolve_duplicates,
            migrations.RunPython.noop,
        ),
        migrations.RunPython(
            ensure_single_primary_phone,
            migrations.RunPython.noop,
        ),
        migrations.RemoveConstraint(
            model_name="user",
            name="unique_user_email",
        ),
        migrations.AddConstraint(
            model_name="user",
            constraint=models.UniqueConstraint(
                Lower("email"),
                condition=(
                    models.Q(("email__isnull", False))
                    & ~models.Q(("email", ""))
                ),
                name="unique_user_email_ci",
            ),
        ),
        migrations.AddConstraint(
            model_name="userphonenumber",
            constraint=models.UniqueConstraint(
                condition=models.Q(("is_primary", True)),
                fields=("user",),
                name="unique_primary_phone_per_user",
            ),
        ),
    ]
