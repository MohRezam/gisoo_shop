from apps.addresses.models import Address


def create_address(*, user, **overrides):
    data = {
        "title": "home",
        "receiver_name": "Mohammadreza",
        "phone_number": "09123456789",
        "province": "Tehran",
        "city": "Tehran",
        "address": "Test Address",
        "postal_code": "1234567890",
    }
    data.update(overrides)
    return Address.objects.create(user=user, **data)
