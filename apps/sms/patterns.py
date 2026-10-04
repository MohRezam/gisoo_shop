from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from django.conf import settings

from apps.sms.exceptions import SmsPatternError

MAX_VAR_LEN = 48


def _clip(value: str) -> str:
    text = str(value or "").strip()
    if len(text) > MAX_VAR_LEN:
        return text[:MAX_VAR_LEN]
    return text


@dataclass(frozen=True)
class SmsPattern:
    key: str
    env_attr: str
    variable_keys: tuple[str, ...]
    panel_text: str
    build_vars: Callable[[dict], list[str]]

    def resolve_body_id(self) -> int:
        raw = getattr(settings, self.env_attr, 0)
        try:
            return int(raw or 0)
        except (TypeError, ValueError):
            return 0


def _vars_from_keys(data: dict, keys: tuple[str, ...]) -> list[str]:
    missing = [k for k in keys if data.get(k) in (None, "")]
    if missing:
        raise SmsPatternError(
            f"Missing pattern variables: {', '.join(missing)}"
        )
    return [_clip(data[k]) for k in keys]


def _otp_vars(data: dict) -> list[str]:
    return _vars_from_keys(data, ("code",))


def _order_amount_vars(data: dict) -> list[str]:
    return _vars_from_keys(data, ("order_id", "amount"))


def _order_id_vars(data: dict) -> list[str]:
    return _vars_from_keys(data, ("order_id",))


def _payment_reminder_vars(data: dict) -> list[str]:
    return _vars_from_keys(data, ("order_id", "minutes_left"))


def _consultation_id_vars(data: dict) -> list[str]:
    return _vars_from_keys(data, ("consultation_id",))


PATTERNS: dict[str, SmsPattern] = {
    "otp_login": SmsPattern(
        key="otp_login",
        env_attr="SMS_OTP_BODY_ID",
        variable_keys=("code",),
        panel_text=(
            "سلام\n"
            "کد ورود تو: {0}\n"
            "این کد را به کسی ندهید.\n"
            "لغو11"
        ),
        build_vars=_otp_vars,
    ),
    "order_created": SmsPattern(
        key="order_created",
        env_attr="SMS_PATTERN_ORDER_CREATED_BODY_ID",
        variable_keys=("order_id", "amount"),
        panel_text=(
            "سفارش شما با شماره {0} به مبلغ {1} تومان ثبت شد.\n"
            "لغو11"
        ),
        build_vars=_order_amount_vars,
    ),
    "payment_success": SmsPattern(
        key="payment_success",
        env_attr="SMS_PATTERN_PAYMENT_SUCCESS_BODY_ID",
        variable_keys=("order_id", "amount"),
        panel_text=(
            "پرداخت سفارش {0} به مبلغ {1} تومان تأیید شد.\n"
            "لغو11"
        ),
        build_vars=_order_amount_vars,
    ),
    "payment_reminder": SmsPattern(
        key="payment_reminder",
        env_attr="SMS_PATTERN_PAYMENT_REMINDER_BODY_ID",
        variable_keys=("order_id", "minutes_left"),
        panel_text=(
            "سفارش {0}: حدود {1} دقیقه تا پایان مهلت پرداخت باقی مانده است.\n"
            "لغو11"
        ),
        build_vars=_payment_reminder_vars,
    ),
    "order_shipped": SmsPattern(
        key="order_shipped",
        env_attr="SMS_PATTERN_ORDER_SHIPPED_BODY_ID",
        variable_keys=("order_id",),
        panel_text=(
            "سفارش {0} ارسال شد.\n"
            "لغو11"
        ),
        build_vars=_order_id_vars,
    ),
    "order_cancelled": SmsPattern(
        key="order_cancelled",
        env_attr="SMS_PATTERN_ORDER_CANCELLED_BODY_ID",
        variable_keys=("order_id",),
        panel_text=(
            "سفارش {0} لغو شد.\n"
            "لغو11"
        ),
        build_vars=_order_id_vars,
    ),
    "delivery_confirm": SmsPattern(
        key="delivery_confirm",
        env_attr="SMS_PATTERN_DELIVERY_CONFIRM_BODY_ID",
        variable_keys=("order_id",),
        panel_text=(
            "سفارش {0} تحویل شده؟ در سایت «تحویل گرفتم» را بزنید.\n"
            "لغو11"
        ),
        build_vars=_order_id_vars,
    ),
    "consultation_answered": SmsPattern(
        key="consultation_answered",
        env_attr="SMS_PATTERN_CONSULTATION_ANSWERED_BODY_ID",
        variable_keys=("consultation_id",),
        panel_text=(
            "پاسخ درخواست مشاوره شما آماده است. شناسه: {0}\n"
            "وارد سایت شوید و نتیجه را ببینید.\n"
            "لغو11"
        ),
        build_vars=_consultation_id_vars,
    ),
    "order_preparing": SmsPattern(
        key="order_preparing",
        env_attr="SMS_PATTERN_ORDER_PREPARING_BODY_ID",
        variable_keys=("order_id",),
        panel_text=(
            "سفارش {0} تأیید شد و در حال آماده‌سازی است.\n"
            "لغو11"
        ),
        build_vars=_order_id_vars,
    ),
    "order_expired": SmsPattern(
        key="order_expired",
        env_attr="SMS_PATTERN_ORDER_EXPIRED_BODY_ID",
        variable_keys=("order_id",),
        panel_text=(
            "مهلت پرداخت سفارش {0} به پایان رسید و سفارش منقضی شد.\n"
            "لغو11"
        ),
        build_vars=_order_id_vars,
    ),
    "payment_rejected": SmsPattern(
        key="payment_rejected",
        env_attr="SMS_PATTERN_PAYMENT_REJECTED_BODY_ID",
        variable_keys=("order_id",),
        panel_text=(
            "رسید پرداخت سفارش {0} رد شد. می‌توانید دوباره پرداخت را ارسال کنید.\n"
            "لغو11"
        ),
        build_vars=_order_id_vars,
    ),
    "consultation_received": SmsPattern(
        key="consultation_received",
        env_attr="SMS_PATTERN_CONSULTATION_RECEIVED_BODY_ID",
        variable_keys=("consultation_id",),
        panel_text=(
            "درخواست مشاوره شما با شناسه {0} ثبت شد. به‌زودی پاسخ داده می‌شود.\n"
            "لغو11"
        ),
        build_vars=_consultation_id_vars,
    ),
}


def get_pattern(pattern_key: str) -> SmsPattern:
    pattern = PATTERNS.get(pattern_key)
    if pattern is None:
        raise SmsPatternError(f"Unknown SMS pattern: {pattern_key}")
    return pattern
