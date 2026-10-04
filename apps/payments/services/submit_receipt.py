import hashlib

from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError

from apps.payments.models import (
    PaymentIntent,
    PaymentIntentStatus,
    PaymentReceipt,
)


MAX_FILE_SIZE = 5 * 1024 * 1024

ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "application/pdf",
}

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".pdf",
}

ALLOWED_STATUSES = {
    PaymentIntentStatus.PENDING_PAYMENT,
    PaymentIntentStatus.RECEIPT_SUBMITTED,
}


def validate_receipt_file(uploaded_file):
    if uploaded_file is None:
        raise ValidationError(
            "Receipt file is required."
        )

    if uploaded_file.size > MAX_FILE_SIZE:
        raise ValidationError(
            "Receipt file must not be larger than 5 MB."
        )

    original_name = uploaded_file.name or ""

    if "." not in original_name:
        raise ValidationError(
            "Receipt file must have a valid extension."
        )

    extension = (
        "."
        + original_name.rsplit(".", 1)[1].lower()
    )

    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            "Only JPG, PNG and PDF receipt files are allowed."
        )

    mime_type = getattr(
        uploaded_file,
        "content_type",
        None,
    )

    if mime_type not in ALLOWED_MIME_TYPES:
        raise ValidationError(
            "Invalid receipt file type."
        )

    uploaded_file.seek(0)

    file_header = uploaded_file.read(8)

    uploaded_file.seek(0)

    valid_signature = False

    if extension in {".jpg", ".jpeg"}:
        valid_signature = file_header.startswith(
            b"\xff\xd8\xff"
        )

    elif extension == ".png":
        valid_signature = file_header.startswith(
            b"\x89PNG\r\n\x1a\n"
        )

    elif extension == ".pdf":
        valid_signature = file_header.startswith(
            b"%PDF-"
        )

    if not valid_signature:
        raise ValidationError(
            "Receipt file content does not match its file type."
        )

    return {
        "original_name": original_name,
        "mime_type": mime_type,
        "file_size": uploaded_file.size,
    }


def calculate_sha256(uploaded_file):
    sha256 = hashlib.sha256()

    for chunk in uploaded_file.chunks():
        sha256.update(chunk)

    uploaded_file.seek(0)

    return sha256.hexdigest()


@transaction.atomic
def submit_receipt(
    *,
    payment_intent_id: int,
    user,
    uploaded_file,
    idempotency_key: str,
):
    if not idempotency_key:
        raise ValidationError(
            "Idempotency-Key header is required."
        )

    idempotency_key = idempotency_key.strip()

    if not idempotency_key:
        raise ValidationError(
            "Idempotency-Key header is required."
        )

    if len(idempotency_key) > 255:
        raise ValidationError(
            "Idempotency-Key must not be longer than 255 characters."
        )

    payment_intent = (
        PaymentIntent.objects
        .select_for_update()
        .select_related("order")
        .filter(
            id=payment_intent_id,
            order__user=user,
        )
        .first()
    )

    if payment_intent is None:
        raise NotFound(
            "Payment intent not found."
        )

    # Idempotent replay
    existing_receipt = (
        PaymentReceipt.objects
        .filter(
            payment_intent=payment_intent,
            idempotency_key=idempotency_key,
        )
        .first()
    )

    if existing_receipt is not None:
        return {
            "receipt": existing_receipt,
            "duplicate": False,
            "idempotent_replay": True,
        }

    # Rejected intents must not accept receipts.
    # Customer creates a new payment intent after rejection.
    if payment_intent.status == PaymentIntentStatus.REJECTED:
        raise ValidationError(
            "This payment was rejected. "
            "Create a new payment intent to try again."
        )

    if payment_intent.status not in ALLOWED_STATUSES:
        raise ValidationError(
            "Receipt cannot be submitted in the current payment status."
        )

    now = timezone.now()

    if payment_intent.expires_at <= now:
        payment_intent.status = PaymentIntentStatus.EXPIRED

        payment_intent.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        raise ValidationError(
            "Payment intent has expired."
        )

    file_data = validate_receipt_file(
        uploaded_file
    )

    sha256 = calculate_sha256(
        uploaded_file
    )

    duplicate_receipt = (
        PaymentReceipt.objects
        .filter(sha256=sha256)
        .exists()
    )

    # Previous receipt is no longer the active receipt.
    PaymentReceipt.objects.filter(
        payment_intent=payment_intent,
        is_active=True,
    ).update(
        is_active=False
    )

    try:
        receipt = PaymentReceipt.objects.create(
            payment_intent=payment_intent,
            file=uploaded_file,
            original_name=file_data["original_name"],
            mime_type=file_data["mime_type"],
            file_size=file_data["file_size"],
            sha256=sha256,
            idempotency_key=idempotency_key,
            is_active=True,
        )

    except IntegrityError:
        receipt = (
            PaymentReceipt.objects
            .filter(
                payment_intent=payment_intent,
                idempotency_key=idempotency_key,
            )
            .first()
        )

        if receipt is None:
            raise

        return {
            "receipt": receipt,
            "duplicate": False,
            "idempotent_replay": True,
        }

    # New receipt starts a new review cycle.
    payment_intent.status = (
        PaymentIntentStatus.RECEIPT_SUBMITTED
    )

    payment_intent.submitted_at = now

    # Previous rejection is no longer relevant.
    payment_intent.rejection_reason = ""

    # Very important:
    # The old review belongs to the previous receipt.
    payment_intent.reviewed_at = None
    payment_intent.reviewed_by = None

    payment_intent.save(
        update_fields=[
            "status",
            "submitted_at",
            "rejection_reason",
            "reviewed_at",
            "reviewed_by",
            "updated_at",
        ]
    )

    try:
        from apps.notifications.models import AdminAlertType
        from apps.notifications.services.admin_alerts import notify_admin

        notify_admin(
            title="رسید پرداخت جدید",
            body=f"سفارش #{payment_intent.order_id} — رسید برای بررسی ارسال شد.",
            type=AdminAlertType.RECEIPT,
            link=f"/admin/payments/paymentintent/{payment_intent.pk}/change/",
        )
    except Exception:
        pass

    return {
        "receipt": receipt,
        "duplicate": duplicate_receipt,
        "idempotent_replay": False,
    }