from datetime import timedelta

from django.utils import timezone

from apps.orders.models import OrderStatus


DEFAULT_ESTIMATED_DAYS_MIN = 3
DEFAULT_ESTIMATED_DAYS_MAX = 5
# After the shipping max estimate (e.g. 5), wait this many more days
# before auto-marking delivered (5 + 5 = 10).
AUTO_DELIVER_EXTRA_DAYS = 5


def get_estimate_bounds(order) -> tuple[int, int]:
    """Return (min_days, max_days) from the order's shipping method."""
    method = getattr(order, "shipping_method", None)
    max_days = getattr(method, "estimated_days", None)
    min_days = getattr(method, "estimated_days_min", None)

    if max_days is None:
        max_days = DEFAULT_ESTIMATED_DAYS_MAX
    if min_days is None:
        min_days = DEFAULT_ESTIMATED_DAYS_MIN

    min_days = max(0, int(min_days))
    max_days = max(min_days, int(max_days))
    return min_days, max_days


def auto_deliver_after_days(order) -> int:
    _, max_days = get_estimate_bounds(order)
    return max_days + AUTO_DELIVER_EXTRA_DAYS


def days_since_shipped(order, *, now=None) -> float | None:
    if order.shipped_at is None:
        return None
    now = now or timezone.now()
    return (now - order.shipped_at).total_seconds() / 86400.0


def customer_can_confirm_delivery(order, *, now=None) -> bool:
    """
    Customer may confirm delivery from the shipping min estimate
    until the auto-deliver deadline (e.g. day 3 through day 10).
    """
    if order.status != OrderStatus.SHIPPED:
        return False
    elapsed = days_since_shipped(order, now=now)
    if elapsed is None:
        return False
    min_days, _ = get_estimate_bounds(order)
    return min_days <= elapsed < auto_deliver_after_days(order)


def should_send_delivery_confirm_sms(order, *, now=None) -> bool:
    if order.status != OrderStatus.SHIPPED:
        return False
    if getattr(order, "delivery_confirm_sms_sent_at", None):
        return False
    elapsed = days_since_shipped(order, now=now)
    if elapsed is None:
        return False
    _, max_days = get_estimate_bounds(order)
    return elapsed >= max_days


def should_auto_deliver(order, *, now=None) -> bool:
    if order.status != OrderStatus.SHIPPED:
        return False
    elapsed = days_since_shipped(order, now=now)
    if elapsed is None:
        return False
    return elapsed >= auto_deliver_after_days(order)


def delivery_confirm_opens_at(order):
    if order.shipped_at is None:
        return None
    min_days, _ = get_estimate_bounds(order)
    return order.shipped_at + timedelta(days=min_days)


def delivery_confirm_sms_at(order):
    if order.shipped_at is None:
        return None
    _, max_days = get_estimate_bounds(order)
    return order.shipped_at + timedelta(days=max_days)


def delivery_auto_at(order):
    if order.shipped_at is None:
        return None
    return order.shipped_at + timedelta(days=auto_deliver_after_days(order))
