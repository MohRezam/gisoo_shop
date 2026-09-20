from celery import shared_task
from django.db import transaction
from django.utils import timezone

from apps.orders.models import Order, OrderStatus
from apps.orders.services.change_order_status import (
    change_order_status,
)
from apps.orders.services.inventory import release_stock
from apps.payments.models import (
    PaymentIntentStatus,
    PaymentStatus,
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
        Order.objects.select_for_update()
        .select_related("payment")
        .prefetch_related("items__variant", "payment_intents")
        .filter(id=order_id)
        .first()
    )

    if order is None:
        return

    if order.status not in (
        OrderStatus.CREATED,
        OrderStatus.WAITING_PAYMENT,
        OrderStatus.PAYMENT_REJECTED,
    ):
        return

    if order.expires_at and order.expires_at > timezone.now():
        return

    # Don't expire if a receipt is already under review or paid
    blocking = order.payment_intents.filter(
        status__in=[
            PaymentIntentStatus.RECEIPT_SUBMITTED,
            PaymentIntentStatus.UNDER_REVIEW,
            PaymentIntentStatus.MANUAL_REVIEW,
            PaymentIntentStatus.PAID,
        ]
    ).exists()
    if blocking:
        return

    payment = getattr(order, "payment", None)
    if payment and payment.status not in (
        PaymentStatus.PENDING,
        PaymentStatus.FAILED,
        PaymentStatus.CANCELED,
    ):
        return

    for item in order.items.all():
        variant = item.variant
        variant.stock += item.quantity
        variant.save(update_fields=["stock"])

    for intent in order.payment_intents.filter(
        status=PaymentIntentStatus.PENDING_PAYMENT
    ):
        intent.status = PaymentIntentStatus.EXPIRED
        intent.save(update_fields=["status", "updated_at"])

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
