from django.contrib.auth import get_user_model

User = get_user_model()


def create_user(
    *,
    phone_number="09120000000",
):
    return User.objects.create_user(
        phone_number=phone_number,
    )