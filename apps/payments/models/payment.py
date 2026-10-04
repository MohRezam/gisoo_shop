import uuid
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shared.models.base import BaseModel


class PaymentIntentStatus(models.TextChoices):
    PENDING_PAYMENT = (
        "pending_payment",
        "در انتظار پرداخت",
    )

    RECEIPT_SUBMITTED = (
        "receipt_submitted",
        "رسید ارسال‌شده",
    )

    PAID = (
        "paid",
        "پرداخت‌شده",
    )

    REJECTED = (
        "rejected",
        "رد شده",
    )

    EXPIRED = (
        "expired",
        "منقضی‌شده",
    )

    REFUNDED = (
        "refunded",
        "بازگشت وجه",
    )


ACTIVE_PAYMENT_INTENT_STATUSES = (
    PaymentIntentStatus.PENDING_PAYMENT,
    PaymentIntentStatus.RECEIPT_SUBMITTED,
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
        verbose_name = "رسید پرداخت"
        verbose_name_plural = "رسیدهای پرداخت"
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
        related_name="payment_intents",
        verbose_name=_("order"),
    )

    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name=_("public token"),
    )

    base_amount_rial = models.PositiveBigIntegerField(
        verbose_name=_("base amount rial"),
        help_text="مبلغ پایه به ریال"
    )

    unique_suffix = models.PositiveSmallIntegerField(
        verbose_name=_("unique suffix"),
    )

    adjustment_discount = models.PositiveIntegerField(
        default=0,
        verbose_name=_("adjustment discount"),
    )

    payable_amount_rial = models.PositiveBigIntegerField(
        verbose_name=_("payable amount rial"),
        help_text="مبلغ پرداختی به ریال"
    )

    destination_card = models.ForeignKey(
        "payments.DestinationCard",
        on_delete=models.PROTECT,
        related_name="payment_intents",
        verbose_name=_("destination card"),
    )

    status = models.CharField(
        max_length=32,
        choices=PaymentIntentStatus.choices,
        default=PaymentIntentStatus.PENDING_PAYMENT,
        verbose_name="وضعیت",
    )

    expires_at = models.DateTimeField(
        verbose_name=_("expires at"),
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("submitted at"),
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("reviewed at"),
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_payment_intents",
        verbose_name=_("reviewed by"),
    )

    rejection_reason = models.TextField(
        blank=True,
        verbose_name=_("rejection reason"),
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("paid at"),
    )

    bank_reference = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("bank reference"),
    )

    class Meta:
        verbose_name = "درخواست پرداخت"
        verbose_name_plural = "درخواست‌های پرداخت"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "destination_card",
                    "payable_amount_rial",
                ],
                condition=models.Q(
                    status__in=ACTIVE_PAYMENT_INTENT_STATUSES
                ),
                name="unique_active_payment_amount_per_card",
            ),
            models.UniqueConstraint(
                fields=["order"],
                condition=models.Q(
                    status__in=ACTIVE_PAYMENT_INTENT_STATUSES
                ),
                name="unique_active_payment_intent_per_order",
            ),
        ]
        indexes = [
            models.Index(
                fields=["status", "created_at"],
                name="pay_intent_status_created_idx",
            ),
            models.Index(
                fields=["expires_at"],
                name="pay_intent_expires_idx",
            ),
        ]

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
        verbose_name = "بررسی پرداخت"
        verbose_name_plural = "بررسی‌های پرداخت"
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Review #{self.pk} "
            f"- PaymentIntent #{self.payment_intent_id}"
        )


class DestinationCard(BaseModel):
    """
    Shop card-to-card destination.

    Only one row should exist site-wide; admin enforces that.
    Employer edits card number, holder name, and optional bank name.
    display_pan / masked_pan are derived automatically.
    """

    name = models.CharField(
        max_length=100,
        verbose_name="نام دارنده",
        help_text="نامی که روی کارت یا در صفحه پرداخت به مشتری نشان داده می‌شود.",
    )

    card_number = models.CharField(
        max_length=16,
        unique=True,
        verbose_name="شماره کارت",
        help_text="۱۶ رقم شماره کارت مقصد (بدون فاصله).",
    )

    bank_name = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="نام بانک",
        help_text="اختیاری — مثلاً ملت، سامان، ملی.",
    )

    display_pan = models.CharField(
        max_length=32,
        blank=True,
        default="",
        verbose_name="شماره کارت (نمایشی)",
    )

    masked_pan = models.CharField(
        max_length=32,
        blank=True,
        default="",
        verbose_name="شماره کارت (ماسک‌شده)",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال در فروشگاه",
        help_text="اگر خاموش باشد، صفحه پرداخت کارت مقصد ندارد.",
    )

    class Meta:
        verbose_name = "کارت مقصد"
        verbose_name_plural = "کارت مقصد"

    def __str__(self):
        from utils.general.card_number_secure import ltr_isolate

        pan = self.display_pan or self.card_number
        if pan:
            return ltr_isolate(pan)
        return "کارت مقصد"

    def _apply_derived_pans(self):
        from utils.general.card_number_secure import (
            format_display_pan,
            normalize_card_number,
            secure_card_number,
        )

        digits = normalize_card_number(self.card_number)
        self.card_number = digits
        self.display_pan = format_display_pan(digits) or digits
        self.masked_pan = secure_card_number(digits) or ""
        self.bank_name = (self.bank_name or "").strip()

    def clean(self):
        from django.core.exceptions import ValidationError

        from utils.general.card_number_secure import normalize_card_number

        digits = normalize_card_number(self.card_number)
        if len(digits) != 16:
            raise ValidationError(
                {"card_number": "شماره کارت باید دقیقاً ۱۶ رقم باشد."}
            )
        self._apply_derived_pans()

        others = DestinationCard.objects.all()
        if self.pk:
            others = others.exclude(pk=self.pk)
        if others.exists():
            raise ValidationError(
                "فقط یک کارت مقصد می‌تواند در سایت وجود داشته باشد. "
                "همان کارت موجود را ویرایش کنید."
            )

    def save(self, *args, **kwargs):
        self._apply_derived_pans()
        super().save(*args, **kwargs)
