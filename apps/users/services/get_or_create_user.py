from apps.users.models import User


def get_or_create_user(phone_number: str):
    user, created = User.objects.get_or_create(
        phone_number=phone_number,
    )

    return user
