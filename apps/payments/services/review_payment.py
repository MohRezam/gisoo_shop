from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from apps.discounts.services import register_discount_usage
from apps.orders.constants import ORDER_EXPIRATION_MINUTES
from apps.orders.models import OrderStatus
from apps.orders.services.change_order_status import (
    change_order_status,
)
from apps.notifications.tasks import send_payment_success_sms
from apps.payments.models import (
    PaymentIntent,
    PaymentIntentStatus,
    PaymentReview,
    PaymentReviewDecision,
)


REVIEWABLE_STATUSES = {
    PaymentIntentStatus.RECEIPT_SUBMITTED,
    PaymentIntentStatus.UNDER_REVIEW,
    PaymentIntentStatus.MANUAL_REVIEW,
}


@transaction.atomic
def approve_payment(
    *,
    payment_intent_id,
    admin,
    bank_verified,
    bank_reference,
    reason="",
):
    payment_intent = (
        PaymentIntent.objects
        .select_for_update()
        .select_related("order")
        .get(pk=payment_intent_id)
    )

    if payment_intent.status == PaymentIntentStatus.PAID:
        return payment_intent

    if payment_intent.status not in REVIEWABLE_STATUSES:
        raise ValidationError(
            _("This payment cannot be approved.")
        )

    if not bank_verified:
        raise ValidationError(
            _("Bank verification is required.")
        )

    bank_reference = (
        bank_reference or ""
    ).strip()

    if not bank_reference:
        raise ValidationError(
            _("Bank reference is required.")
        )

    now = timezone.now()

    payment_intent.status = (
        PaymentIntentStatus.PAID
    )

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
        reason=reason,
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
        .get(pk=payment_intent_id)
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

    # After rejection, the customer gets a new
    # 15-minute window to submit another receipt.
    new_expiration = (
        now
        + timedelta(
            minutes=ORDER_EXPIRATION_MINUTES
        )
    )

    payment_intent.status = (
        PaymentIntentStatus.REJECTED
    )

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