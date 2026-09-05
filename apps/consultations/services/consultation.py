from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.consultations.models.consultation import (
    ConsultationRequest,
    GuestDeviceAccess,
    GuestIdentity,
)


GUEST_ACCESS_TOKEN_LIFETIME = timedelta(
    days=30,
)


def normalize_phone_number(phone_number):
    """
    Normalize Iranian mobile numbers
    to 09xxxxxxxxx format.
    """

    phone_number = phone_number.strip()

    if phone_number.startswith("+98"):
        phone_number = "0" + phone_number[3:]

    elif phone_number.startswith("0098"):
        phone_number = "0" + phone_number[4:]

    return phone_number


def get_or_create_guest(phone_number):
    phone_number = normalize_phone_number(
        phone_number,
    )

    guest, _ = GuestIdentity.objects.get_or_create(
        phone_number=phone_number,
    )

    return guest


def create_guest_device_access(guest):
    """
    Create a new guest access token.

    A new token is created for each new guest
    device/browser flow.
    """

    return GuestDeviceAccess.objects.create(
        guest=guest,
        expires_at=(
            timezone.now()
            + GUEST_ACCESS_TOKEN_LIFETIME
        ),
    )


def get_guest_by_token(token):
    """
    Return the guest associated with a valid
    and non-expired access token.
    """

    if not token:
        return None

    access = (
        GuestDeviceAccess.objects
        .select_related("guest")
        .filter(
            token=token,
        )
        .first()
    )

    if access is None:
        return None

    if access.expires_at <= timezone.now():
        return None

    access.last_used_at = timezone.now()

    access.save(
        update_fields=[
            "last_used_at",
        ],
    )

    return access.guest


def has_active_consultation(*, user=None, guest=None):
    """
    Check whether the user or guest has
    a pending consultation.
    """

    queryset = ConsultationRequest.objects.filter(
        status=ConsultationRequest.Status.PENDING,
    )

    if user is not None:
        return queryset.filter(
            user=user,
        ).exists()

    if guest is not None:
        return queryset.filter(
            guest=guest,
        ).exists()

    return False


@transaction.atomic
def merge_guest_consultations_after_login(user):
    """
    Attach guest consultations with the same
    phone number to the authenticated user.
    """

    phone_number = normalize_phone_number(
        user.phone_number,
    )

    guest = (
        GuestIdentity.objects
        .filter(
            phone_number=phone_number,
        )
        .first()
    )

    if not guest:
        return 0

    updated_count = (
        ConsultationRequest.objects
        .filter(
            guest=guest,
            user__isnull=True,
        )
        .update(
            user=user,
            guest=None,
        )
    )

    return updated_count