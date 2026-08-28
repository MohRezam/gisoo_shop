from django.db import migrations


def migrate_existing_phone_numbers(apps, schema_editor):
    User = apps.get_model("users", "User")
    UserPhoneNumber = apps.get_model(
        "users",
        "UserPhoneNumber",
    )

    for user in User.objects.exclude(
        phone_number__isnull=True
    ).exclude(
        phone_number=""
    ):
        UserPhoneNumber.objects.get_or_create(
            user=user,
            phone_number=user.phone_number,
            defaults={
                "is_verified": True,
                "is_primary": True,
            },
        )


def reverse_migrate_existing_phone_numbers(
    apps,
    schema_editor,
):
    UserPhoneNumber = apps.get_model(
        "users",
        "UserPhoneNumber",
    )

    UserPhoneNumber.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_user_birthdate"),
    ]

    operations = [
        migrations.RunPython(
            migrate_existing_phone_numbers,
            reverse_migrate_existing_phone_numbers,
        ),
    ]