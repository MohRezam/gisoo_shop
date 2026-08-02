from uuid import uuid4

from django.core.cache import cache

from core_gisoo_backend import settings
from core_gisoo_backend.settings.components.constants import CHANGE_PHONE_PREFIX


def map_phone_number_to_request_id(
    phone_number: str, request_type: str, prefix: str = "prefix", exp=settings.OTP_TTL
) -> str:
    """Sets cache with the prefix `request_type` but only returns the request id"""
    request_id = str(uuid4())
    cache.set(f"{request_type}_{prefix}_{request_id}", phone_number, timeout=exp)
    return request_id


def get_phone_number_from_request_id(
    request_id: str, request_type: str, prefix: str = "prefix"
) -> str:
    return cache.get(f"{request_type}_{prefix}_{request_id}")


def get_prefix_otp_ttl(type_: str):
    from apps.users.serializers.token import AuthType

    try:
        if type_ and AuthType.CHANGE_PHONE == AuthType(type_):
            return CHANGE_PHONE_PREFIX, settings.OTP_TTL * 2
        return "prefix", settings.OTP_TTL
    except Exception:
        return "prefix", settings.OTP_TTL
