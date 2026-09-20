import uuid
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shared.models.base import BaseModel


class PaymentStatus(models.TextChoices):
    PENDING = (
        "pending",
        "در انتظار",
    )

    PROCESSING = (
        "processing",
        "در حال پردازش",
    )

    SUCCESS = (
        "success",
        "موفق",
    )

    FAILED = (
        "failed",
        "ناموفق",
    )

    CANCELED = (
        "canceled",
        "لغو شده",
    )


ACTIVE_PAYMENT_INTENT_STATUSES = (
    PaymentIntentStatus.PENDING_PAYMENT,
    PaymentIntentStatus.RECEIPT_SUBMITTED,
    PaymentIntentStatus.UNDER_REVIEW,
    PaymentIntentStatus.MANUAL_REVIEW,
)


class PaymentReceipt(BaseModel):
    payment_intent = models.ForeignKey(
        "payments.PaymentIntent",
        on_delete=models.CASCADE,
        related_name="receipts",
        verbose_name=_("payment intent"),
    )

    file = models.FileField(
        upload_to="payments/receipts/%Y/%m/",
        verbose_name=_("file"),
    )

    original_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("original name"),
    )

    mime_type = models.CharField(
        max_length=100,
        verbose_name=_("mime type"),
    )

    file_size = models.PositiveBigIntegerField(
        verbose_name=_("file size"),
    )

    sha256 = models.CharField(
        max_length=64,
        db_index=True,
        verbose_name=_("SHA-256"),
    )

    idempotency_key = models.CharField(
        max_length=255,
        verbose_name=_("idempotency key"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("is active"),
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("uploaded at"),
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["payment_intent", "idempotency_key"],
                name="unique_receipt_idempotency_per_intent",
            ),
        ]
        indexes = [
            models.Index(
                fields=["payment_intent", "is_active"],
                name="pay_receipt_intent_active_idx",
            ),
            models.Index(
                fields=["sha256"],
                name="pay_receipt_sha256_idx",
            ),
        ]


class PaymentIntent(BaseModel):
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.PROTECT,
        related_name="payment",
        verbose_name="سفارش",
    )

    amount = models.PositiveBigIntegerField(
        verbose_name="مبلغ",
    )

    status = models.CharField(
        max_length=32,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        verbose_name="وضعیت",
    )

    gateway_payment_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="شناسه پرداخت درگاه",
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="شناسه مرجع درگاه",
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان پرداخت",
    )

    bank_reference = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("bank reference"),
    )

    class Meta:
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداخت‌ها"

    def __str__(self):
        return (
            f"PaymentIntent #{self.pk} "
            f"- Order #{self.order_id} "
            f"- {self.payable_amount_rial}"
        )


class PaymentReviewDecision(models.TextChoices):
    APPROVED = (
        "approved",
        _("Approved"),
    )

    REJECTED = (
        "rejected",
        _("Rejected"),
    )

    MANUAL_REVIEW = (
        "manual_review",
        _("Manual review"),
    )


class PaymentReview(BaseModel):
    payment_intent = models.ForeignKey(
        PaymentIntent,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("payment intent"),
    )

    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="payment_reviews",
        verbose_name=_("admin"),
    )

    decision = models.CharField(
        max_length=32,
        choices=PaymentReviewDecision.choices,
        verbose_name=_("decision"),
    )

    bank_reference = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("bank reference"),
    )

    reason = models.TextField(
        blank=True,
        verbose_name=_("reason"),
    )
    bank_verified = models.BooleanField(
        default=False,
        verbose_name=_("bank verified"),
    )

    class Meta:
        verbose_name = _("payment review")
        verbose_name_plural = _("payment reviews")
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Review #{self.pk} "
            f"- PaymentIntent #{self.payment_intent_id}"
        )


class DestinationCard(BaseModel):
    name = models.CharField(
        max_length=100,
        verbose_name=_("name"),
    )

    card_number = models.CharField(
        max_length=16,
        unique=True,
        verbose_name=_("card number"),
    )

    display_pan = models.CharField(
        max_length=32,
        verbose_name=_("display pan"),
    )

    masked_pan = models.CharField(
        max_length=32,
        verbose_name=_("masked pan"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("is active"),
    )

    class Meta:
        verbose_name = _("destination card")
        verbose_name_plural = _("destination cards")

    def __str__(self):
        return self.display_pan
