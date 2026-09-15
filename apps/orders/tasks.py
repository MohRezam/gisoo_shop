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
from apps.orders.services.inventory import release_stock
from apps.payments.models import (
    PaymentIntent,
    PaymentIntentStatus,
)


@shared_task
@transaction.atomic
def expire_order(
    order_id: int,
):
    order = (
        Order.objects
        .select_for_update()
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

    payment_intent = (
        PaymentIntent.objects
        .select_for_update()
        .filter(
            order=order,
            status__in=[
                PaymentIntentStatus.PENDING_PAYMENT,
                PaymentIntentStatus.RECEIPT_SUBMITTED,
                PaymentIntentStatus.UNDER_REVIEW,
                PaymentIntentStatus.MANUAL_REVIEW,
            ],
        )
        .first()
    )

    if payment_intent is not None:
        payment_intent.status = PaymentIntentStatus.EXPIRED
        payment_intent.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

    variants = [
        (
            item.variant,
            item.quantity,
        )
        for item in order.items.all()
    ]

    release_stock(
        variants=variants,
    )

    change_order_status(
        order=order,
        new_status=OrderStatus.EXPIRED,
        reason="Order expired automatically.",
    )

@shared_task
def expire_overdue_orders():
    overdue_order_ids = list(
        Order.objects.filter(
            status=OrderStatus.CREATED,
            expires_at__lte=timezone.now(),
        ).values_list(
            "id",
            flat=True,
        )
    )

    for order_id in overdue_order_ids:
        expire_order.delay(order_id)

    return len(overdue_order_ids)