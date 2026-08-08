import random

from apps.shared.utils.redis import redis_client


def generate_otp() -> str:
    return str(random.randint(1000, 9999))


def save_otp(phone_number: str, code: str) -> None:
    redis_client.setex(
        f"otp:{phone_number}",
        120,
        code,
    )


def get_otp(phone_number: str):
    return redis_client.get(
        f"otp:{phone_number}"
    )


def delete_otp(phone_number: str):
    redis_client.delete(
        f"otp:{phone_number}"
    )
