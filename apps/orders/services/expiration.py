from django.db import transaction

from apps.orders.constants import ORDER_EXPIRATION_MINUTES
from apps.orders.tasks import expire_order


def schedule_order_expiration(
        *,
        order,
):
    transaction.on_commit(
        lambda: expire_order.apply_async(
            args=[order.id],
            countdown=ORDER_EXPIRATION_MINUTES * 60,
        )
    )
