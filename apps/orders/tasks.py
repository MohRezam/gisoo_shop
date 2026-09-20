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


def get_order_reserved_variants(*, order):
    """
    Return all product variants whose stock was reserved
    by this order.

    Includes:
    - normal OrderItems
    - products contained inside OrderBundles
    """

    variants = []

    # ---------------------------------------------------------
    # Normal products
    # ---------------------------------------------------------

    for item in order.items.all():
        variants.append(
            (
                item.variant,
                item.quantity,
            )
        )

    # ---------------------------------------------------------
    # Bundle products
    # ---------------------------------------------------------
    #
    # OrderBundle.quantity = number of bundles purchased
    #
    # OrderBundle.bundle_quantity = number of product units
    # contained in one bundle.
    #
    # Therefore:
    #
    # reserved_quantity =
    #     bundle_quantity * quantity
    #
    # Example:
    #
    # Bundle contains 3 shampoos
    # Customer buys 2 bundles
    #
    # reserved stock = 3 * 2 = 6
    #

    for bundle in order.bundles.all():
        reserved_quantity = (
            bundle.bundle_quantity
            * bundle.quantity
        )

        variants.append(
            (
                bundle.variant,
                reserved_quantity,
            )
        )

    return variants


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
    # If a receipt was submitted before the deadline,
    # the customer has completed their part.
    #
    # Therefore the order must remain active while
    # admin reviews the payment.
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
    # If the customer did not submit a new receipt during
    # the retry window, the order expires.
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

    # ---------------------------------------------------------
    # RELEASE STOCK
    # ---------------------------------------------------------
    #
    # This now includes BOTH:
    #
    # 1. normal products
    # 2. products contained inside bundles
    #

    variants = get_order_reserved_variants(
        order=order
    )

    release_stock(
        variants=variants
    )

    # ---------------------------------------------------------
    # EXPIRE ORDER
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