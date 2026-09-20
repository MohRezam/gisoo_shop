from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from apps.orders.models import OrderStatus
from apps.orders.services.change_order_status import change_order_status
from apps.payments.models import PaymentIntent, PaymentIntentStatus
from apps.notifications.services.inbox import notify_user
from apps.payments.cache import invalidate_payment_intent_token_cache
from apps.orders.cache import invalidate_track_order_cache


@transaction.atomic
def approve_payment_intent(*, intent: PaymentIntent, reviewed_by=None, reason: str = ""):
    intent = (
        PaymentIntent.objects.select_for_update()
        .select_related("order", "destination_card")
        .get(pk=intent.pk)
    )

    if intent.status not in (
        PaymentIntentStatus.RECEIPT_SUBMITTED,
        PaymentIntentStatus.UNDER_REVIEW,
        PaymentIntentStatus.MANUAL_REVIEW,
    ):
        raise ValidationError(_("Intent is not awaiting review."))

    intent.status = PaymentIntentStatus.PAID
    intent.reviewed_at = timezone.now()
    intent.reviewed_by = reviewed_by
    intent.save(update_fields=["status", "reviewed_at", "reviewed_by", "updated_at"])

    change_order_status(
        order=intent.order,
        new_status=OrderStatus.PREPARING,
        changed_by=reviewed_by,
        reason=reason or "Payment receipt approved.",
    )

    notify_user(
        user=intent.order.user,
        title="پرداخت تأیید شد",
        body=f"رسید پرداخت سفارش {intent.order.public_number or intent.order_id} تأیید شد.",
        type="order",
        link=f"/account/orders/{intent.order_id}",
        order_id=intent.order_id,
    )
    invalidate_payment_intent_token_cache(intent.token)
    invalidate_track_order_cache(intent.order.public_number, intent.order.phone_number)
    return intent


@transaction.atomic
def reject_payment_intent(
    *,
    intent: PaymentIntent,
    reviewed_by=None,
    reason: str = "",
):
    intent = (
        PaymentIntent.objects.select_for_update()
        .select_related("order", "destination_card")
        .get(pk=intent.pk)
    )

    if intent.status not in (
        PaymentIntentStatus.RECEIPT_SUBMITTED,
        PaymentIntentStatus.UNDER_REVIEW,
        PaymentIntentStatus.MANUAL_REVIEW,
        PaymentIntentStatus.PENDING_PAYMENT,
    ):
        raise ValidationError(_("Intent cannot be rejected in this status."))

    intent.status = PaymentIntentStatus.REJECTED
    intent.rejection_reason = reason or ""
    intent.reviewed_at = timezone.now()
    intent.reviewed_by = reviewed_by
    intent.save(
        update_fields=[
            "status",
            "rejection_reason",
            "reviewed_at",
            "reviewed_by",
            "updated_at",
        ]
    )

    change_order_status(
        order=intent.order,
        new_status=OrderStatus.PAYMENT_REJECTED,
        changed_by=reviewed_by,
        reason=reason or "Payment receipt rejected.",
    )

    notify_user(
        user=intent.order.user,
        title="رسید پرداخت رد شد",
        body=(
            f"رسید پرداخت سفارش {intent.order.public_number or intent.order_id} رد شد. "
            "می‌توانید دوباره پرداخت را ارسال کنید."
        ),
        type="order",
        link=f"/account/orders/{intent.order_id}",
        order_id=intent.order_id,
    )
    invalidate_payment_intent_token_cache(intent.token)
    invalidate_track_order_cache(intent.order.public_number, intent.order.phone_number)
    return intent
