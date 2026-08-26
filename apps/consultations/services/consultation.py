import random
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.consultations.models.consultation import GuestIdentity, GuestDeviceAccess, GuestOTP, ConsultationRequest

OTP_EXPIRATION_MINUTES = 2


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


def get_or_create_device_access(guest):
    access = (
        GuestDeviceAccess.objects
        .filter(guest=guest)
        .order_by("-last_used_at")
        .first()
    )

    if access:
        return access

    return GuestDeviceAccess.objects.create(
        guest=guest,
    )


@transaction.atomic
def create_guest_otp(phone_number):
    guest = get_or_create_guest(
        phone_number,
    )

    GuestOTP.objects.filter(
        guest=guest,
        is_used=False,
    ).update(
        is_used=True,
    )

    # code = str(
    #     random.randint(
    #         100000,
    #         999999,
    #     )
    # )

    code = str(123456)

    otp = GuestOTP.objects.create(
        guest=guest,
        code=code,
        expires_at=(
                timezone.now()
                + timedelta(
            minutes=OTP_EXPIRATION_MINUTES,
        )
        ),
    )

    return guest, otp


def verify_guest_otp(
    phone_number,
    code,
):
    phone_number = normalize_phone_number(
        phone_number,
    )

    guest = GuestIdentity.objects.filter(
        phone_number=phone_number,
    ).first()

    if not guest:
        return None, "invalid"

    otp = (
        GuestOTP.objects
        .filter(
            guest=guest,
            is_used=False,
        )
        .order_by("-created_at")
        .first()
    )

    if not otp:
        return None, "invalid"

    if otp.attempts >= 5:
        return None, "too_many_attempts"

    if otp.expires_at < timezone.now():
        return None, "expired"

    if otp.code != code:
        otp.attempts += 1

        otp.save(
            update_fields=[
                "attempts",
            ],
        )

        return None, "invalid"

    otp.is_used = True

    otp.save(
        update_fields=[
            "is_used",
        ],
    )

    device_access = GuestDeviceAccess.objects.create(
        guest=guest,
    )

    return device_access, None


def has_active_consultation(guest):
    return (
        ConsultationRequest.objects
        .filter(
            guest=guest,
            status__in=[
                ConsultationRequest.Status.PENDING,
                ConsultationRequest.Status.REVIEWING,
            ],
        )
        .exists()
    )
