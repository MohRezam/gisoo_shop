from celery import shared_task
from django.db import transaction
from django.utils import timezone

from apps.orders.models import (
    Order,
    OrderStatus,
)
from apps.orders.services.change_order_status import (
    change_order_status,
)
from apps.payments.models import (
    PaymentStatus,
)


@shared_task
@transaction.atomic
def expire_order(
    order_id: int,
):
    order = (
        Order.objects
        .select_for_update()
        .select_related(
            "payment",
        )
        .prefetch_related(
            "items__variant",
        )
        .filter(
            id=order_id,
        )
        .first()
    )

    if order is None:
        return

    if order.status != OrderStatus.CREATED:
        return

    if order.expires_at > timezone.now():
        return

    if order.payment.status != PaymentStatus.PENDING:
        return

    for item in order.items.all():
        variant = item.variant

        variant.stock += item.quantity

        variant.save(
            update_fields=[
                "stock",
            ]
        )

    change_order_status(
        order=order,
        new_status=OrderStatus.EXPIRED,
        reason="Order expired automatically.",
    )