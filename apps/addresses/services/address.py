from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from apps.addresses.models import Address

User = get_user_model()


@transaction.atomic
def create_address(*, user, **data):
    # Lock the user row so concurrent creates cannot both become default.
    User.objects.select_for_update().filter(pk=user.pk).get()

    has_address = Address.objects.filter(
        user=user,
        archived=False,
    ).exists()

    if not has_address:
        Address.objects.filter(
            user=user,
            is_default=True,
        ).update(
            is_default=False,
        )

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
    if address.user_id != user.id:
        raise ValidationError(
            _("Address does not belong to this user.")
        )

    if address.archived:
        raise ValidationError(
            _("Cannot set an archived address as default.")
        )

    list(
        Address.objects.select_for_update().filter(
            user=user,
            archived=False,
        )
    )

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
        next_address = (
            Address.objects
            .select_for_update()
            .filter(
                user=user,
                archived=False,
            )
            .order_by("-created_at")
            .first()
        )

        if next_address:
            next_address.is_default = True

            next_address.save(
                update_fields=["is_default"]
            )
