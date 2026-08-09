from apps.addresses.models import Address


def create_address(
    *,
    user,
):
    return Address.objects.create(
        user=user,
        receiver_name="Mohammadreza",
        phone_number="09123456789",
        province="Tehran",
        city="Tehran",
        address="Test Address",
        postal_code="1234567890",
    )