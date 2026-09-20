from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from apps.payments.models import PaymentIntent, PaymentIntentStatus


@transaction.atomic
def upload_payment_receipt(*, intent: PaymentIntent, receipt, idempotency_key: str = ""):
    intent = (
        PaymentIntent.objects.select_for_update()
        .select_related("destination_card", "order")
        .get(pk=intent.pk)
    )

    if idempotency_key:
        existing = (
            PaymentIntent.objects.filter(
                order_id=intent.order_id,
                idempotency_key=idempotency_key,
            )
            .exclude(pk=intent.pk)
            .select_related("destination_card", "order")
            .first()
        )
        if existing:
            return existing
        if intent.idempotency_key == idempotency_key and intent.receipt_image:
            return intent

    if intent.status != PaymentIntentStatus.PENDING_PAYMENT:
        raise ValidationError(_("Receipt can only be uploaded for pending payment intents."))

    if intent.expires_at and intent.expires_at < timezone.now():
        intent.status = PaymentIntentStatus.EXPIRED
        intent.save(update_fields=["status", "updated_at"])
        raise ValidationError(_("Payment intent has expired."))

    intent.receipt_image = receipt
    intent.receipt_uploaded_at = timezone.now()
    intent.status = PaymentIntentStatus.RECEIPT_SUBMITTED
    if idempotency_key:
        intent.idempotency_key = idempotency_key

    intent.save(
        update_fields=[
            "receipt_image",
            "receipt_uploaded_at",
            "status",
            "idempotency_key",
            "updated_at",
        ]
    )

    # Move to under_review immediately for admin queue visibility
    intent.status = PaymentIntentStatus.UNDER_REVIEW
    intent.save(update_fields=["status", "updated_at"])

    return intent
