from django.db import transaction
from django.utils import timezone

from apps.orders.tasks import expire_order


def schedule_order_expiration(
        *,
        order,
):
    if order.expires_at is not None:
        countdown = max(
            1,
            int((order.expires_at - timezone.now()).total_seconds()),
        )
    else:
        from apps.payments.services.checkout_settings import (
            get_payment_expiration_minutes,
        )

        countdown = get_payment_expiration_minutes() * 60

    transaction.on_commit(
        lambda: expire_order.apply_async(
            args=[order.id],
            countdown=countdown,
        )
    )
