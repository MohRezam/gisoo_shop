from apps.addresses.models import Address
from django.db import transaction


def create_address(*, user, **data):
    has_address = Address.objects.filter(
        user=user
    ).exists()

    address = Address.objects.create(
        user=user,
        is_default=not has_address,
        **data,
    )

    return address


@transaction.atomic
def set_default_address(
        *,
        user,
        address,
):
    Address.objects.filter(
        user=user,
        is_default=True,
    ).update(
        is_default=False,
    )

    address.is_default = True

    address.save(
        update_fields=["is_default"]
    )


@transaction.atomic
def delete_address(
        *,
        address: Address,
):
    user = address.user
    was_default = address.is_default

    address.delete()

    if was_default:
        next_address = Address.objects.filter(
            user=user
        ).order_by(
            "-created_at"
        ).first()

        if next_address:
            next_address.is_default = True

            next_address.save(
                update_fields=["is_default"]
            )
