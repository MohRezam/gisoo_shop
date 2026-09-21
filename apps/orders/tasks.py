from celery import shared_task
from django.db import transaction
from django.utils import timezone

from apps.orders.models import Order, OrderStatus
from apps.orders.services.change_order_status import (
    change_order_status,
)
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

REVIEW_PENDING_STATUSES = {
    PaymentIntentStatus.RECEIPT_SUBMITTED,
    PaymentIntentStatus.UNDER_REVIEW,
    PaymentIntentStatus.MANUAL_REVIEW,
}

EXPIRABLE_ORDER_STATUSES = {
    OrderStatus.CREATED,
    OrderStatus.WAITING_PAYMENT,
    OrderStatus.PAYMENT_REJECTED,
}


def has_valid_payment_receipt(
    *,
    order,
    expires_at,
):
    """
    If the customer submitted a receipt before the
    original payment deadline, the order must not
    expire while the payment is waiting for review.
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
            "bundles",
        )
        .filter(id=order_id)
        .first()
    )

    if order is None:
        return

    if order.status not in EXPIRABLE_ORDER_STATUSES:
        return

    now = timezone.now()

    if order.expires_at is None or order.expires_at > now:
        return

    # ---------------------------------------------------------
    # WAITING_PAYMENT / CREATED
    # ---------------------------------------------------------
    #
    # If a receipt was submitted before the deadline,
    # the customer has completed their part.
    #
    # Therefore the order must remain active while
    # admin reviews the payment.
    #

    if order.status in {
        OrderStatus.CREATED,
        OrderStatus.WAITING_PAYMENT,
    }:
        if has_valid_payment_receipt(
            order=order,
            expires_at=order.expires_at,
        ):
            return

    # ---------------------------------------------------------
    # PAYMENT INTENT (lock after Order to avoid deadlocks)
    # ---------------------------------------------------------
    #
    # Lock the latest relevant intent and re-check under
    # select_for_update so a concurrent receipt submit
    # cannot race with expiration.
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
        # Race guard: receipt submitted / awaiting review
        # after the initial check must skip expire.
        if payment_intent.status in REVIEW_PENDING_STATUSES:
            return

        if has_valid_payment_receipt(
            order=order,
            expires_at=order.expires_at,
        ):
            return

        payment_intent.status = (
            PaymentIntentStatus.EXPIRED
        )

        payment_intent.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

    # ---------------------------------------------------------
    # EXPIRE ORDER (releases stock via change_order_status)
    # ---------------------------------------------------------

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
            status__in=list(EXPIRABLE_ORDER_STATUSES),
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
