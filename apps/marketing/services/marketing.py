import random

from django.core.cache import cache


OTP_TIMEOUT = 2 * 60
OTP_PREFIX = "marketing:otp:"


def generate_otp():
    return str(random.randint(100000, 999999))


def get_otp_key(phone_number):
    return f"{OTP_PREFIX}{phone_number}"


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