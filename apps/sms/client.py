from __future__ import annotations

import logging
import re
from typing import Any
from xml.etree import ElementTree

import requests
from django.conf import settings

logger = logging.getLogger("sms")

ERROR_MESSAGES_FA = {
    0: "نام کاربری یا رمز عبور اشتباه است.",
    1: "دسترسی وب‌سرویس پیامک غیرفعال است.",
    2: "در هر درخواست فقط یک شماره مجاز است.",
    3: "خط ارسالی در پنل تعریف نشده است.",
    4: "شناسه الگو (bodyId) اشتباه یا هنوز تأیید نشده است.",
    5: "تعداد یا ترتیب متغیرهای الگو با پنل همخوان نیست.",
    6: "خطای داخلی پنل پیامک.",
    7: "در متن متغیر کلمهٔ فیلترشده وجود دارد.",
    10: "لینک در متغیرهای پیامک مجاز نیست.",
    11: "پیامک ارسال نشد.",
    12: "مدارک کاربر در پنل کامل نیست.",
    18: "شماره موبایل نامعتبر است.",
    19: "سقف ارسال روزانه پر شده است.",
    108: "IP به‌خاطر تلاش ناموفق بلاک شده است.",
    109: "تنظیم IP مجاز در پنل الزامی است.",
    110: "باید ApiKey به‌جای رمز عبور استفاده شود.",
}


def normalize_iran_mobile(phone: str) -> str:
    """Normalize to 09xxxxxxxxx."""
    digits = re.sub(r"\D", "", str(phone or ""))
    if digits.startswith("98") and len(digits) >= 12:
        digits = "0" + digits[2:]
    if len(digits) == 10 and digits.startswith("9"):
        digits = "0" + digits
    return digits


def is_valid_iran_mobile(phone: str) -> bool:
    normalized = normalize_iran_mobile(phone)
    return bool(re.fullmatch(r"09\d{9}", normalized))


def parse_soap_result(raw: str) -> str:
    text = (raw or "").strip()
    if not text:
        return ""

    for tag in (
        "SendByBaseNumberResult",
        "GetCreditResult",
        "string",
    ):
        match = re.search(
            rf"<{tag}[^>]*>([^<]*)</{tag}>",
            text,
            flags=re.IGNORECASE,
        )
        if match:
            return match.group(1).strip()

    try:
        root = ElementTree.fromstring(text)
        leaves = [
            (node.text or "").strip()
            for node in root.iter()
            if (node.text or "").strip()
        ]
        if leaves:
            return leaves[-1]
    except ElementTree.ParseError:
        pass

    return text


def interpret_send_result(raw_value: str) -> dict[str, Any]:
    """
    Positive large number → success message id.
    Negative number → provider error code.
    """
    value = (raw_value or "").strip()
    try:
        number = int(value)
    except (TypeError, ValueError):
        return {
            "success": False,
            "message_id": None,
            "error_code": None,
            "error_message": f"پاسخ نامعتبر پنل: {value[:200]}",
        }

    if number > 0 and (number >= 1000 or len(str(abs(number))) >= 6):
        return {
            "success": True,
            "message_id": str(number),
            "error_code": None,
            "error_message": None,
        }

    if number > 0:
        # Small positive values are unusual; treat as success id anyway.
        return {
            "success": True,
            "message_id": str(number),
            "error_code": None,
            "error_message": None,
        }

    code = abs(number)
    return {
        "success": False,
        "message_id": None,
        "error_code": code,
        "error_message": ERROR_MESSAGES_FA.get(
            code,
            f"خطای پنل پیامک (کد {code}).",
        ),
    }


def _credentials() -> tuple[str, str]:
    username = str(getattr(settings, "SMS_USERNAME", "") or "").strip()
    password = str(getattr(settings, "SMS_PASSWORD", "") or "").strip()
    return username, password


def send_by_base_number(
    phone: str,
    body_id: int,
    text_vars: list[str],
) -> dict[str, Any]:
    """
    POST SendByBaseNumber with repeated ``text`` form fields.
    """
    normalized = normalize_iran_mobile(phone)
    empty = {
        "success": False,
        "message_id": None,
        "phone": normalized,
        "provider_response": "",
        "error_message": None,
        "error_code": None,
    }

    username, password = _credentials()
    if not username or not password:
        empty["error_message"] = (
            "تنظیمات SMS_USERNAME / SMS_PASSWORD خالی است؛ ارسال انجام نشد."
        )
        logger.warning(
            "SMS skipped (missing credentials) to=%s bodyId=%s vars=%s",
            normalized,
            body_id,
            text_vars,
        )
        return empty

    if not body_id:
        empty["error_message"] = (
            "bodyId الگو تنظیم نشده است؛ ارسال انجام نشد."
        )
        logger.warning(
            "SMS skipped (missing bodyId) to=%s vars=%s",
            normalized,
            text_vars,
        )
        return empty

    if not is_valid_iran_mobile(normalized):
        empty["error_message"] = ERROR_MESSAGES_FA[18]
        empty["error_code"] = 18
        return empty

    soap_url = str(
        getattr(
            settings,
            "SMS_SOAP_URL",
            "http://api.payamak-panel.com/post/Send.asmx/SendByBaseNumber",
        )
        or "http://api.payamak-panel.com/post/Send.asmx/SendByBaseNumber"
    ).strip()

    form_data: list[tuple[str, str]] = [
        ("username", username),
        ("password", password),
        ("to", normalized),
        ("bodyId", str(int(body_id))),
    ]
    for value in text_vars:
        form_data.append(("text", str(value)))

    try:
        response = requests.post(
            soap_url,
            data=form_data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            timeout=15,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        logger.exception(
            "Melipayamak SendByBaseNumber transport error to=%s bodyId=%s: %s",
            normalized,
            body_id,
            exc,
        )
        empty["error_message"] = f"خطا در ارتباط با پنل پیامک: {exc}"
        empty["provider_response"] = str(exc)
        return empty

    provider_raw = response.text or ""
    parsed = parse_soap_result(provider_raw)
    outcome = interpret_send_result(parsed)

    result = {
        "success": outcome["success"],
        "message_id": outcome["message_id"],
        "phone": normalized,
        "provider_response": parsed or provider_raw[:500],
        "error_message": outcome["error_message"],
        "error_code": outcome["error_code"],
    }

    if result["success"]:
        logger.info(
            "SMS sent to=%s bodyId=%s vars=%s messageId=%s",
            normalized,
            body_id,
            text_vars,
            result["message_id"],
        )
    else:
        logger.error(
            "SMS failed to=%s bodyId=%s vars=%s code=%s error=%s raw=%s",
            normalized,
            body_id,
            text_vars,
            result["error_code"],
            result["error_message"],
            result["provider_response"],
        )

    return result


def get_credit() -> dict[str, Any]:
    """Optional credit check via Actions.asmx/GetCredit."""
    username, password = _credentials()
    if not username or not password:
        return {
            "success": False,
            "credit": None,
            "error_message": "تنظیمات SMS خالی است.",
        }

    url = str(
        getattr(
            settings,
            "SMS_CREDIT_URL",
            "https://api.payamak-panel.com/post/Actions.asmx/GetCredit",
        )
        or "https://api.payamak-panel.com/post/Actions.asmx/GetCredit"
    ).strip()

    try:
        response = requests.post(
            url,
            data={
                "username": username,
                "password": password,
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            timeout=15,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        return {
            "success": False,
            "credit": None,
            "error_message": str(exc),
        }

    parsed = parse_soap_result(response.text or "")
    try:
        credit = float(parsed)
    except (TypeError, ValueError):
        return {
            "success": False,
            "credit": None,
            "error_message": f"پاسخ اعتبار نامعتبر: {parsed[:200]}",
            "provider_response": parsed,
        }

    return {
        "success": True,
        "credit": credit,
        "error_message": None,
        "provider_response": parsed,
    }
