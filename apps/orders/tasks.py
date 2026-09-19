from celery import shared_task
from django.db import transaction
from django.utils import timezone

from apps.orders.models import Order, OrderStatus
from apps.orders.services.change_order_status import (
    change_order_status,
)
from apps.orders.services.inventory import release_stock
from apps.payments.models import (
    PaymentIntent,
    PaymentIntentStatus,
)


ACTIVE_PAYMENT_STATUSES = [
    PaymentIntentStatus.PENDING_PAYMENT,
    PaymentIntentStatus.RECEIPT_SUBMITTED,
    PaymentIntentStatus.UNDER_REVIEW,
    PaymentIntentStatus.MANUAL_REVIEW,
]


def has_valid_payment_receipt(
    *,
    order,
    expires_at,
):
    """
    A receipt submitted before the original deadline
    protects the order from automatic expiration.

    Once the customer has submitted a receipt,
    expiration is no longer based on the customer.
    """

    return PaymentIntent.objects.filter(
        order=order,
        status__in=[
            PaymentIntentStatus.RECEIPT_SUBMITTED,
            PaymentIntentStatus.UNDER_REVIEW,
            PaymentIntentStatus.MANUAL_REVIEW,
        ],
        submitted_at__isnull=False,
        submitted_at__lte=expires_at,
    ).exists()


@shared_task
@transaction.atomic
def expire_order(order_id: int):
    order = (
        Order.objects
        .select_for_update()
        .prefetch_related(
            "items__variant",
        )
        .filter(id=order_id)
        .first()
    )

    if order is None:
        return

    if order.status not in {
        OrderStatus.CREATED,
        OrderStatus.PAYMENT_REJECTED,
    }:
        return

    now = timezone.now()

    if order.expires_at > now:
        return

    # ---------------------------------------------------------
    # CREATED
    # ---------------------------------------------------------
    #
    # If the customer submitted a valid receipt before
    # the deadline, don't expire the order.
    #
    if order.status == OrderStatus.CREATED:

        if has_valid_payment_receipt(
            order=order,
            expires_at=order.expires_at,
        ):
            return

    # ---------------------------------------------------------
    # PAYMENT_REJECTED
    # ---------------------------------------------------------
    #
    # Here we intentionally DO NOT check for a receipt.
    #
    # If the order is still PAYMENT_REJECTED when its
    # retry deadline passes, it means the customer didn't
    # submit a new receipt.
    #
    # Therefore the order must expire.
    #

    payment_intent = (
        PaymentIntent.objects
        .select_for_update()
        .filter(
            order=order,
            status__in=(
                ACTIVE_PAYMENT_STATUSES
                + [
                    PaymentIntentStatus.REJECTED,
                ]
            ),
        )
        .order_by("-created_at")
        .first()
    )

    if payment_intent is not None:

        payment_intent.status = (
            PaymentIntentStatus.EXPIRED
        )

        payment_intent.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

    # Release the stock reserved for this order.
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
    now = timezone.now()

    overdue_order_ids = list(
        Order.objects
        .filter(
            status__in=[
                OrderStatus.CREATED,
                OrderStatus.PAYMENT_REJECTED,
            ],
            expires_at__lte=now,
        )
        .values_list(
            "id",
            flat=True,
        )
    )

    for order_id in overdue_order_ids:
        expire_order.delay(order_id)

    return len(overdue_order_ids)