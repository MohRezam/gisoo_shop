from django.db import transaction

from apps.consultations.models.consultation import (
    ConsultationRequest,
    GuestIdentity,
)


def normalize_phone_number(phone_number):
    """
    Normalize Iranian mobile numbers to 09xxxxxxxxx format.
    """

    phone_number = phone_number.strip()

    if phone_number.startswith("+98"):
        phone_number = "0" + phone_number[3:]

    elif phone_number.startswith("0098"):
        phone_number = "0" + phone_number[4:]

    return phone_number


def get_or_create_guest(phone_number):
    phone_number = normalize_phone_number(
        phone_number
    )

    guest, _ = GuestIdentity.objects.get_or_create(
        phone_number=phone_number,
    )

    return guest


def has_active_consultation(*, user=None, guest=None):
    queryset = ConsultationRequest.objects.filter(
        status__in=[
            ConsultationRequest.Status.PENDING,
            ConsultationRequest.Status.REVIEWING,
        ],
    )

    if user is not None:
        return queryset.filter(user=user).exists()

    if guest is not None:
        return queryset.filter(guest=guest).exists()

    return False


@transaction.atomic
def merge_guest_consultations_after_login(user):
    """
    Attach guest consultations with the same phone number
    to the authenticated user so they appear in /my/.
    """

    phone_number = normalize_phone_number(
        user.phone_number
    )

    guest = GuestIdentity.objects.filter(
        phone_number=phone_number,
    ).first()

    if not guest:
        return 0

    return (
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
