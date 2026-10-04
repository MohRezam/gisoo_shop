from __future__ import annotations

import logging
from typing import Any

from django.conf import settings

from apps.sms.client import send_by_base_number
from apps.sms.exceptions import SmsPatternError
from apps.sms.patterns import get_pattern

logger = logging.getLogger("sms")


def send_pattern_sms(
    pattern_key: str,
    phone: str,
    data: dict | None = None,
) -> dict[str, Any]:
    """
    High-level API: resolve bodyId from env, build vars, send via panel.
    Never hardcode bodyId at call sites — always pass ``pattern_key``.
    """
    data = data or {}
    try:
        pattern = get_pattern(pattern_key)
    except SmsPatternError as exc:
        logger.error("SMS pattern error: %s", exc)
        return {
            "success": False,
            "message_id": None,
            "phone": phone,
            "provider_response": "",
            "error_message": str(exc),
            "error_code": None,
            "pattern_key": pattern_key,
        }

    body_id = pattern.resolve_body_id()
    try:
        text_vars = pattern.build_vars(data)
    except SmsPatternError as exc:
        logger.error(
            "SMS vars error pattern=%s: %s",
            pattern_key,
            exc,
        )
        return {
            "success": False,
            "message_id": None,
            "phone": phone,
            "provider_response": "",
            "error_message": str(exc),
            "error_code": None,
            "pattern_key": pattern_key,
        }

    logger.info(
        "SMS send_pattern key=%s bodyId=%s to=%s vars=%s",
        pattern_key,
        body_id,
        phone,
        text_vars,
    )

    result = send_by_base_number(
        phone=phone,
        body_id=body_id,
        text_vars=text_vars,
    )
    result["pattern_key"] = pattern_key
    return result


def send_otp(phone: str, code: str) -> dict[str, Any]:
    result = send_pattern_sms(
        "otp_login",
        phone,
        {"code": code},
    )

    # Dev convenience: never leak OTP in production.
    if (
        not result.get("success")
        and getattr(settings, "DEBUG", False)
        and not getattr(settings, "SMS_ENABLED", False)
    ):
        logger.info(
            "DEBUG OTP for %s (SMS disabled): %s",
            phone,
            code,
        )

    return result
