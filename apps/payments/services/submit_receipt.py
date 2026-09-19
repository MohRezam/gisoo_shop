import hashlib

from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError

from apps.orders.models import OrderStatus
from apps.orders.services.change_order_status import (
    change_order_status,
)
from apps.payments.models import (
    PaymentIntent,
    PaymentIntentStatus,
    PaymentReceipt,
)


MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

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
    PaymentIntentStatus.UNDER_REVIEW,
    PaymentIntentStatus.MANUAL_REVIEW,
    PaymentIntentStatus.REJECTED,
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

    extension = "." + original_name.rsplit(
        ".",
        1,
    )[1].lower()

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

    # ---------------------------------------------------------
    # File signature / magic bytes validation
    # ---------------------------------------------------------

    uploaded_file.seek(0)

    file_header = uploaded_file.read(8)

    uploaded_file.seek(0)

    valid_signature = False

    if extension in {
        ".jpg",
        ".jpeg",
    }:
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
    # ---------------------------------------------------------
    # Idempotency-Key validation
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Get payment intent
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Idempotency replay
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Payment state validation
    # ---------------------------------------------------------

    if payment_intent.status not in ALLOWED_STATUSES:
        raise ValidationError(
            "Receipt cannot be submitted in the current payment status."
        )

    now = timezone.now()

    # ---------------------------------------------------------
    # Rejected payment can be resubmitted
    # ---------------------------------------------------------

    is_resubmission = (
        payment_intent.status
        == PaymentIntentStatus.REJECTED
    )

    # ---------------------------------------------------------
    # Expiration
    #
    # Normal payments must not accept receipts after expiry.
    #
    # Rejected payments are an exception because the customer
    # is allowed to correct the rejected receipt and submit
    # a new one.
    # ---------------------------------------------------------

    if (
        not is_resubmission
        and payment_intent.expires_at <= now
    ):
        payment_intent.status = (
            PaymentIntentStatus.EXPIRED
        )

        payment_intent.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        raise ValidationError(
            "Payment intent has expired."
        )

    # ---------------------------------------------------------
    # File validation
    # ---------------------------------------------------------

    file_data = validate_receipt_file(
        uploaded_file,
    )

    # ---------------------------------------------------------
    # SHA-256
    # ---------------------------------------------------------

    sha256 = calculate_sha256(
        uploaded_file,
    )

    duplicate_receipt = (
        PaymentReceipt.objects
        .filter(
            sha256=sha256,
        )
        .exists()
    )

    # ---------------------------------------------------------
    # Deactivate previous active receipt
    # ---------------------------------------------------------

    PaymentReceipt.objects.filter(
        payment_intent=payment_intent,
        is_active=True,
    ).update(
        is_active=False,
    )

    # ---------------------------------------------------------
    # Create new receipt
    # ---------------------------------------------------------

    try:
        receipt = PaymentReceipt.objects.create(
            payment_intent=payment_intent,
            file=uploaded_file,
            original_name=file_data[
                "original_name"
            ],
            mime_type=file_data[
                "mime_type"
            ],
            file_size=file_data[
                "file_size"
            ],
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

    # ---------------------------------------------------------
    # Change payment status
    # ---------------------------------------------------------

    payment_intent.status = (
        PaymentIntentStatus.RECEIPT_SUBMITTED
    )

    payment_intent.submitted_at = now

    payment_intent.rejection_reason = ""
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

    # ---------------------------------------------------------
    # Rejected order becomes active again
    # ---------------------------------------------------------

    order = payment_intent.order

    if (
        is_resubmission
        and order.status == OrderStatus.PAYMENT_REJECTED
    ):
        change_order_status(
            order=order,
            new_status=OrderStatus.CREATED,
            reason=(
                "Customer resubmitted payment receipt."
            ),
        )

    return {
        "receipt": receipt,
        "duplicate": duplicate_receipt,
        "idempotent_replay": False,
    }