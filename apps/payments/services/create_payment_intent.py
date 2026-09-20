from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from apps.orders.models import Order, OrderStatus
from apps.orders.services.change_order_status import change_order_status
from apps.payments.constants import (
    PAYMENT_DESTINATION_CARD_ID,
    PAYMENT_INTENT_EXPIRATION_MINUTES,
    DEFAULT_DESTINATION_BANK_NAME,
    DEFAULT_DESTINATION_CARD_NUMBER,
    DEFAULT_DESTINATION_HOLDER_NAME,
)
from apps.payments.cache import (
    get_cached_destination_card_id,
    set_cached_destination_card_id,
)
from apps.payments.models import (
    PaymentDestinationCard,
    PaymentIntent,
    PaymentIntentStatus,
    ACTIVE_INTENT_STATUSES,
    RECREATE_ALLOWED_STATUSES,
)


def get_active_destination_card():
    cached_id = get_cached_destination_card_id()
    if cached_id:
        card = PaymentDestinationCard.objects.filter(
            pk=cached_id,
            is_active=True,
        ).first()
        if card:
            return card

    if PAYMENT_DESTINATION_CARD_ID:
        card = PaymentDestinationCard.objects.filter(
            pk=PAYMENT_DESTINATION_CARD_ID,
            is_active=True,
        ).first()
        if card:
            set_cached_destination_card_id(card.id)
            return card

    card = PaymentDestinationCard.objects.filter(is_active=True).order_by("-id").first()
    if card:
        set_cached_destination_card_id(card.id)
        return card

    card, _ = PaymentDestinationCard.objects.get_or_create(
        card_number=DEFAULT_DESTINATION_CARD_NUMBER,
        defaults={
            "bank_name": DEFAULT_DESTINATION_BANK_NAME,
            "holder_name": DEFAULT_DESTINATION_HOLDER_NAME,
            "is_active": True,
        },
    )
    if not card.is_active:
        card.is_active = True
        card.save(update_fields=["is_active"])
    set_cached_destination_card_id(card.id)
    return card


@transaction.atomic
def create_payment_intent(*, order: Order, user=None):
    """
    Create or resume a C2C payment intent.

    - Returns existing active intent (pending / receipt / review).
    - Allows a new intent when latest is rejected or expired.
    - Rejects when already paid or order is not payable.
    """
    order = Order.objects.select_for_update().get(pk=order.pk)

    if user is not None and order.user_id != user.id:
        raise ValidationError(_("Order not found."))

    if order.status in (
        OrderStatus.CANCELED,
        OrderStatus.EXPIRED,
        OrderStatus.DELIVERED,
        OrderStatus.SHIPPED,
        OrderStatus.PREPARING,
    ):
        raise ValidationError(_("Cannot create payment intent for this order."))

    active = (
        order.payment_intents.filter(status__in=ACTIVE_INTENT_STATUSES)
        .select_related("destination_card", "order")
        .order_by("-created_at")
        .first()
    )
    if active:
        return active, False

    latest = order.payment_intents.order_by("-created_at").first()
    if latest and latest.status == PaymentIntentStatus.PAID:
        raise ValidationError(_("Order is already paid."))

    if latest and latest.status not in RECREATE_ALLOWED_STATUSES:
        raise ValidationError(
            _("Cannot recreate payment intent for status '%(status)s'.")
            % {"status": latest.status}
        )

    destination = get_active_destination_card()
    intent = PaymentIntent.objects.create(
        order=order,
        destination_card=destination,
        payable_amount=order.total_price,
        status=PaymentIntentStatus.PENDING_PAYMENT,
        expires_at=timezone.now()
        + timedelta(minutes=PAYMENT_INTENT_EXPIRATION_MINUTES),
    )

    if order.status != OrderStatus.WAITING_PAYMENT:
        change_order_status(
            order=order,
            new_status=OrderStatus.WAITING_PAYMENT,
            changed_by=user,
            reason="Payment intent created.",
        )

    intent = (
        PaymentIntent.objects.select_related("destination_card", "order")
        .get(pk=intent.pk)
    )
    return intent, True
