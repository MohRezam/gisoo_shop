import random
from django.core.cache import cache


def generate_otp() -> str:
    return str(random.randint(1000, 9999))


OTP_TIMEOUT = 2 * 60


def get_otp_key(phone_number):
    return f"marketing:otp:{phone_number}"


def save_otp(phone_number, otp):
    cache.set(
        get_otp_key(phone_number),
        otp,
        timeout=OTP_TIMEOUT,
    )


def get_otp(phone_number):
    return cache.get(
        get_otp_key(phone_number)
    )


def delete_otp(phone_number):
    cache.delete(
        get_otp_key(phone_number)
    )
