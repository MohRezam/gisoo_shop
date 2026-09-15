import secrets
from datetime import timedelta

from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.orders.models import Order, OrderStatus
from apps.payments.models import (
    ACTIVE_PAYMENT_INTENT_STATUSES,
    DestinationCard,
    PaymentIntent,
    PaymentIntentStatus,
)


MIN_SUFFIX = 100
MAX_SUFFIX = 999
MAX_SUFFIX_ATTEMPTS = 20


def get_payment_expiration(order: Order):
    """
    Returns the expiration time for the payment intent.

    The order expiration is the source of truth when available.
    Otherwise, ORDER_EXPIRATION_MINUTES is used.
    """

    if order.expires_at is not None:
        return order.expires_at

    expiration_minutes = getattr(
        settings,
        "ORDER_EXPIRATION_MINUTES",
        60,
    )

    return timezone.now() + timedelta(
        minutes=expiration_minutes
    )


def get_destination_card():
    """
    Returns the currently active destination card for payments.
    """

    card = (
        DestinationCard.objects
        .filter(
            is_active=True,
        )
        .order_by("id")
        .first()
    )

    if card is None:
        raise ValidationError(
            "Payment destination card is not available."
        )

    return card



def generate_unique_amount(
    *,
    base_amount_rial: int,
    destination_card: DestinationCard,
):
    if base_amount_rial <= 0:
        raise ValidationError(
            "Order amount must be greater than zero."
        )

    if base_amount_rial < MIN_SUFFIX:
        raise ValidationError(
            "Order amount is too small for unique payment amount generation."
        )

    # ---------------------------------------------------------
    # Get all currently used active payment amounts
    # ---------------------------------------------------------

    used_amounts = set(
        PaymentIntent.objects.filter(
            destination_card=destination_card,
            status__in=ACTIVE_PAYMENT_INTENT_STATUSES,
        ).values_list(
            "payable_amount_rial",
            flat=True,
        )
    )

    # ---------------------------------------------------------
    # Generate all possible suffixes
    # ---------------------------------------------------------

    suffixes = list(
        range(
            MIN_SUFFIX,
            MAX_SUFFIX + 1,
        )
    )

    # Randomize candidates so payment amounts are not predictable.
    secrets.SystemRandom().shuffle(suffixes)

    # ---------------------------------------------------------
    # Find an available amount
    # ---------------------------------------------------------

    for suffix in suffixes:
        adjustment_discount = (
            base_amount_rial - suffix
        ) % 1000

        payable_amount_rial = (
            base_amount_rial
            - adjustment_discount
        )

        if payable_amount_rial <= 0:
            continue

        if payable_amount_rial in used_amounts:
            continue

        return {
            "unique_suffix": suffix,
            "adjustment_discount": adjustment_discount,
            "payable_amount_rial": payable_amount_rial,
        }

    raise ValidationError(
        "Unable to generate a unique payment amount. "
        "All available payment amounts are currently in use."
    )


@transaction.atomic
def create_payment_intent(*, order_id: int, user):
    order = (
        Order.objects
        .select_for_update()
        .filter(
            id=order_id,
            user=user,
        )
        .first()
    )

    if order is None:
        raise ValidationError("Order not found.")

    if order.status != OrderStatus.CREATED:
        raise ValidationError(
            "Payment is not available for this order."
        )

    now = timezone.now()

    existing_intent = (
        PaymentIntent.objects
        .select_related(
            "destination_card",
            "order",
        )
        .filter(
            order=order,
            status__in=ACTIVE_PAYMENT_INTENT_STATUSES,
        )
        .first()
    )

    if existing_intent is not None:
        if existing_intent.expires_at <= now:
            existing_intent.status = PaymentIntentStatus.EXPIRED
            existing_intent.save(
                update_fields=["status"]
            )

        else:
            return existing_intent

    if order.expires_at is not None and order.expires_at <= now:
        raise ValidationError(
            "Order payment time has expired."
        )

    destination_card = get_destination_card()

    expiration = get_payment_expiration(order)

    amount_data = generate_unique_amount(
        base_amount_rial=order.total_price,
        destination_card=destination_card,
    )

    for _ in range(MAX_SUFFIX_ATTEMPTS):
        try:
            with transaction.atomic():
                payment_intent = PaymentIntent.objects.create(
                    order=order,
                    base_amount_rial=order.total_price,
                    unique_suffix=amount_data["unique_suffix"],
                    adjustment_discount=amount_data[
                        "adjustment_discount"
                    ],
                    payable_amount_rial=amount_data[
                        "payable_amount_rial"
                    ],
                    destination_card=destination_card,
                    status=PaymentIntentStatus.PENDING_PAYMENT,
                    expires_at=expiration,
                )

            return payment_intent

        except IntegrityError:
            existing_intent = (
                PaymentIntent.objects
                .select_related(
                    "destination_card",
                    "order",
                )
                .filter(
                    order=order,
                    status__in=ACTIVE_PAYMENT_INTENT_STATUSES,
                )
                .first()
            )

            if existing_intent is not None:
                return existing_intent

            amount_data = generate_unique_amount(
                base_amount_rial=order.total_price,
                destination_card=destination_card,
            )

    raise ValidationError(
        "Unable to create payment intent. Please try again."
    )