from apps.orders.constants import ORDER_EXPIRATION_MINUTES
from apps.payments.models import ShopCheckoutSettings


def get_checkout_settings() -> ShopCheckoutSettings:
    obj, _created = ShopCheckoutSettings.objects.get_or_create(pk=1)
    return obj


def get_payment_expiration_minutes() -> int:
    try:
        minutes = int(get_checkout_settings().payment_expiration_minutes)
    except Exception:
        minutes = ORDER_EXPIRATION_MINUTES
    if minutes < 1:
        return ORDER_EXPIRATION_MINUTES
    return minutes


def payment_terms_lines() -> list[str]:
    settings = get_checkout_settings()
    text = (settings.terms or "").strip()
    if not text:
        return []
    return [line.strip() for line in text.splitlines() if line.strip()]


def payment_support_url() -> str:
    return (get_checkout_settings().support_url or "").strip()


def enforce_order_amount_limits(total_toman: int) -> None:
    from rest_framework.exceptions import ValidationError

    settings = get_checkout_settings()
    minimum = settings.min_order_amount or 0
    maximum = settings.max_order_amount or 0
    if minimum and total_toman < minimum:
        raise ValidationError(
            f"حداقل مبلغ خرید {minimum:,} تومان است.".replace(",", "،")
        )
    if maximum and total_toman > maximum:
        raise ValidationError(
            f"حداکثر مبلغ خرید {maximum:,} تومان است.".replace(",", "،")
        )
