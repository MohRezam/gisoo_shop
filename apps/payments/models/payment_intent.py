import secrets
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shared.models.base import BaseModel
from core_gisoo_backend.storage_backends.locations import payment_receipt_path


class PaymentIntentStatus(models.TextChoices):
    PENDING_PAYMENT = "pending_payment", "در انتظار پرداخت"
    RECEIPT_SUBMITTED = "receipt_submitted", "رسید ارسال شده"
    UNDER_REVIEW = "under_review", "در حال بررسی"
    MANUAL_REVIEW = "manual_review", "بررسی دستی"
    PAID = "paid", "پرداخت شده"
    REJECTED = "rejected", "رد شده"
    EXPIRED = "expired", "منقضی شده"
    REFUNDED = "refunded", "بازپرداخت شده"


ACTIVE_INTENT_STATUSES = (
    PaymentIntentStatus.PENDING_PAYMENT,
    PaymentIntentStatus.RECEIPT_SUBMITTED,
    PaymentIntentStatus.UNDER_REVIEW,
    PaymentIntentStatus.MANUAL_REVIEW,
)

TERMINAL_INTENT_STATUSES = (
    PaymentIntentStatus.PAID,
    PaymentIntentStatus.REJECTED,
    PaymentIntentStatus.EXPIRED,
    PaymentIntentStatus.REFUNDED,
)

RECREATE_ALLOWED_STATUSES = (
    PaymentIntentStatus.REJECTED,
    PaymentIntentStatus.EXPIRED,
)


def generate_payment_intent_token():
    return secrets.token_urlsafe(24)


class PaymentIntent(BaseModel):
    """
    Card-to-card payment intent for an order.

    Amounts (payable_amount) are stored in تومان (IRT / toman).
    """

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="payment_intents",
        verbose_name="سفارش",
    )
    destination_card = models.ForeignKey(
        "payments.PaymentDestinationCard",
        on_delete=models.PROTECT,
        related_name="payment_intents",
        verbose_name="کارت مقصد",
    )
    token = models.CharField(
        max_length=64,
        unique=True,
        default=generate_payment_intent_token,
        editable=False,
        verbose_name="توکن",
    )
    status = models.CharField(
        max_length=32,
        choices=PaymentIntentStatus.choices,
        default=PaymentIntentStatus.PENDING_PAYMENT,
        db_index=True,
        verbose_name="وضعیت",
    )
    payable_amount = models.PositiveBigIntegerField(
        verbose_name="مبلغ قابل پرداخت (تومان)",
    )
    expires_at = models.DateTimeField(
        verbose_name="تاریخ انقضا",
    )
    receipt_image = models.ImageField(
        upload_to=payment_receipt_path(),
        blank=True,
        null=True,
        verbose_name="تصویر رسید",
    )
    receipt_uploaded_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان آپلود رسید",
    )
    rejection_reason = models.TextField(
        blank=True,
        verbose_name="دلیل رد",
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان بررسی",
    )
    reviewed_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_payment_intents",
        verbose_name="بررسی‌کننده",
    )
    idempotency_key = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name="کلید تکرارناپذیری",
    )

    class Meta:
        verbose_name = "درخواست پرداخت"
        verbose_name_plural = "درخواست‌های پرداخت"
        ordering = ["-created_at"]

    def __str__(self):
        return f"PaymentIntent #{self.pk} ({self.status})"

    @property
    def can_upload_receipt(self):
        return self.status == PaymentIntentStatus.PENDING_PAYMENT

    @property
    def public_number(self):
        return getattr(self.order, "public_number", None)
