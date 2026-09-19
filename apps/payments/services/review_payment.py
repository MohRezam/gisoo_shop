from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.discounts.services import register_discount_usage
from apps.notifications.tasks import send_payment_success_sms
from apps.orders.constants import ORDER_EXPIRATION_MINUTES
from apps.orders.models import Order, OrderStatus
from apps.orders.services.change_order_status import change_order_status

from apps.payments.models import (
    PaymentIntent,
    PaymentIntentStatus,
    PaymentReview,
    PaymentReviewDecision,
)
from apps.orders.services.inventory import reserve_stock
from django.utils.translation import gettext_lazy as _

REVIEWABLE_STATUSES = {
    PaymentIntentStatus.RECEIPT_SUBMITTED,
    PaymentIntentStatus.UNDER_REVIEW,
    PaymentIntentStatus.MANUAL_REVIEW,
}


@transaction.atomic
def approve_payment(
        *,
        payment_intent_id: int,
        admin,
        bank_verified: bool,
        bank_reference: str,
        reason: str = "",
):
    """
    Approve a payment after the admin has verified the actual
    bank transaction.

    This function is idempotent:
    approving an already-paid payment does not create another
    PaymentReview.
    """

    payment_intent = (
        PaymentIntent.objects
        .select_for_update()
        .select_related("order")
        .get(pk=payment_intent_id)
    )

    # Idempotency
    if payment_intent.status == PaymentIntentStatus.PAID:
        return payment_intent

    if payment_intent.status not in REVIEWABLE_STATUSES:
        raise ValidationError(
            "This payment cannot be approved in its current status."
        )

    if not bank_verified:
        raise ValidationError(
            "Bank transaction must be verified before approval."
        )

    bank_reference = (bank_reference or "").strip()

    if not bank_reference:
        raise ValidationError(
            "Bank reference is required."
        )

    now = timezone.now()

    payment_intent.status = PaymentIntentStatus.PAID
    payment_intent.reviewed_at = now
    payment_intent.reviewed_by = admin
    payment_intent.paid_at = now
    payment_intent.bank_reference = bank_reference
    payment_intent.rejection_reason = ""

    payment_intent.save(
        update_fields=[
            "status",
            "reviewed_at",
            "reviewed_by",
            "paid_at",
            "bank_reference",
            "rejection_reason",
            "updated_at",
        ]
    )

    PaymentReview.objects.create(
        payment_intent=payment_intent,
        admin=admin,
        decision=PaymentReviewDecision.APPROVED,
        bank_reference=bank_reference,
        reason=reason or "",
        bank_verified=True,
    )

    order = payment_intent.order

    if order.discount_id is not None:
        register_discount_usage(
            discount=order.discount,
            user=order.user,
            order=order,
        )

    if order.status == OrderStatus.CREATED:
        change_order_status(
            order=order,
            new_status=OrderStatus.PREPARING,
            changed_by=admin,
            reason="Payment approved.",
        )

    transaction.on_commit(
        lambda: send_payment_success_sms.delay(
            user_id=order.user_id,
            recipient=order.phone_number,
            order_id=order.id,
            amount=order.total_price,
        )
    )

    return payment_intent


@transaction.atomic
def reject_payment(
    *,
    payment_intent_id,
    admin,
    reason,
):
    payment_intent = (
        PaymentIntent.objects
        .select_for_update()
        .select_related("order")
        .get(
            pk=payment_intent_id,
        )
    )

    if payment_intent.status == PaymentIntentStatus.REJECTED:
        return payment_intent

    if payment_intent.status not in REVIEWABLE_STATUSES:
        raise ValidationError(
            _("This payment cannot be rejected.")
        )

    reason = (reason or "").strip()

    if not reason:
        raise ValidationError(
            _("Rejection reason is required.")
        )

    now = timezone.now()

    new_expiration = (
        now
        + timedelta(
            minutes=ORDER_EXPIRATION_MINUTES,
        )
    )

    payment_intent.status = PaymentIntentStatus.REJECTED
    payment_intent.reviewed_at = now
    payment_intent.reviewed_by = admin
    payment_intent.rejection_reason = reason
    payment_intent.expires_at = new_expiration

    payment_intent.save(
        update_fields=[
            "status",
            "reviewed_at",
            "reviewed_by",
            "rejection_reason",
            "expires_at",
            "updated_at",
        ]
    )

    PaymentReview.objects.create(
        payment_intent=payment_intent,
        admin=admin,
        decision=PaymentReviewDecision.REJECTED,
        reason=reason,
        bank_verified=False,
    )

    order = payment_intent.order

    if order.status == OrderStatus.CREATED:
        order.expires_at = new_expiration

        order.save(
            update_fields=[
                "expires_at",
                "updated_at",
            ]
        )

        change_order_status(
            order=order,
            new_status=OrderStatus.PAYMENT_REJECTED,
            changed_by=admin,
            reason="Payment receipt rejected.",
        )

    return payment_intent


@transaction.atomic
def reopen_payment(
        *,
        payment_intent_id: int,
        admin,
        reason: str,
):
    """
    Reopen an expired/rejected/manual-review payment.

    If the related order is expired, its stock is reserved again
    and the order is moved back to the created state.

    A new payment window is created from the current time.
    """

    payment_intent = (
        PaymentIntent.objects
        .select_for_update()
        .select_related("order")
        .get(pk=payment_intent_id)
    )

    if payment_intent.status == PaymentIntentStatus.PENDING_PAYMENT:
        return payment_intent

    allowed_statuses = {
        PaymentIntentStatus.EXPIRED,
        PaymentIntentStatus.REJECTED,
        PaymentIntentStatus.MANUAL_REVIEW,
    }

    if payment_intent.status not in allowed_statuses:
        raise ValidationError(
            "This payment cannot be reopened in its current status."
        )

    reason = (reason or "").strip()

    if not reason:
        raise ValidationError(
            "Reopen reason is required."
        )

    order = (
        Order.objects
        .select_for_update()
        .prefetch_related("items__variant")
        .get(pk=payment_intent.order_id)
    )

    if order.status not in {
        OrderStatus.CREATED,
        OrderStatus.EXPIRED,
    }:
        raise ValidationError(
            "Only created or expired orders can be reopened."
        )

    now = timezone.now()

    # اگر سفارش expired شده، موجودی آن قبلاً آزاد شده است.
    # بنابراین قبل از reopen باید دوباره موجودی رزرو شود.
    if order.status == OrderStatus.EXPIRED:
        variants = [
            (item.variant, item.quantity)
            for item in order.items.all()
        ]

        reserve_stock(
            variants=variants,
        )

        change_order_status(
            order=order,
            new_status=OrderStatus.CREATED,
            changed_by=admin,
            reason=f"Order reopened: {reason}",
        )

    new_expiration = now + timedelta(
        minutes=ORDER_EXPIRATION_MINUTES,
    )

    payment_intent.status = PaymentIntentStatus.PENDING_PAYMENT
    payment_intent.expires_at = new_expiration
    payment_intent.submitted_at = None
    payment_intent.reviewed_at = None
    payment_intent.reviewed_by = None
    payment_intent.rejection_reason = ""
    payment_intent.paid_at = None
    payment_intent.bank_reference = ""

    payment_intent.save(
        update_fields=[
            "status",
            "expires_at",
            "submitted_at",
            "reviewed_at",
            "reviewed_by",
            "rejection_reason",
            "paid_at",
            "bank_reference",
            "updated_at",
        ]
    )

    PaymentReview.objects.create(
        payment_intent=payment_intent,
        admin=admin,
        decision=PaymentReviewDecision.MANUAL_REVIEW,
        reason=f"Reopened: {reason}",
        bank_verified=False,
    )

    return payment_intent
