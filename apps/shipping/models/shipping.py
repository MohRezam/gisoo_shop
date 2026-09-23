from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shared.models.base import BaseModel


class ShippingCarrier(models.TextChoices):
    POST = (
        "post",
        "پست",
    )
    TIPAX = (
        "tipax",
        "تیپاکس",
    )


CARRIER_TRACKING_URLS = {
    ShippingCarrier.POST: "https://tracking.post.ir/",
    ShippingCarrier.TIPAX: "https://tipaxco.com/tracking",
}

CARRIER_SHIPPED_LABELS = {
    ShippingCarrier.POST: "ارسال با پست",
    ShippingCarrier.TIPAX: "ارسال با تیپاکس",
}


class ShippingMethod(BaseModel):
    title = models.CharField(
        verbose_name="عنوان",
        max_length=255,
        unique=True,
    )

    carrier = models.CharField(
        max_length=16,
        choices=ShippingCarrier.choices,
        default=ShippingCarrier.POST,
        verbose_name="حامل",
    )

    price = models.PositiveBigIntegerField(
        verbose_name="قیمت",
        default=0,
    )

    free_shipping_minimum = models.PositiveBigIntegerField(
        verbose_name="حداقل ارسال رایگان",
        default=0,
        help_text="۰ یعنی ارسال رایگان غیرفعال است.",
    )

    estimated_days_min = models.PositiveSmallIntegerField(
        verbose_name="حداقل روز تخمینی",
        default=3,
        help_text="شروع بازه تحویل (مثلاً ۳ در «۳ تا ۵ روز»).",
    )

    estimated_days = models.PositiveSmallIntegerField(
        verbose_name="حداکثر روز تخمینی",
        default=5,
        help_text="پایان بازه تحویل و زمان پیامک تأیید تحویل (مثلاً ۵).",
    )

    is_active = models.BooleanField(
        verbose_name="فعال",
        default=True,
    )

    class Meta:
        verbose_name = "روش ارسال"
        verbose_name_plural = "روش‌های ارسال"
        ordering = [
            "price",
        ]

    def __str__(self):
        return self.title

    @property
    def tracking_url(self) -> str:
        return CARRIER_TRACKING_URLS.get(
            self.carrier,
            CARRIER_TRACKING_URLS[ShippingCarrier.POST],
        )


class ShipmentStatus(models.TextChoices):
    PENDING = (
        "pending",
        "در انتظار",
    )

    SHIPPED = (
        "shipped",
        "ارسال شده",
    )

    DELIVERED = (
        "delivered",
        "تحویل شده",
    )

    RETURNED = (
        "returned",
        "مرجوع شده",
    )


class Shipment(BaseModel):
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="shipments",
        verbose_name="سفارش",
    )

    status = models.CharField(
        max_length=20,
        choices=ShipmentStatus.choices,
        default=ShipmentStatus.PENDING,
        verbose_name="وضعیت",
    )

    tracking_code = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="کد پیگیری",
    )

    shipped_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان ارسال",
    )

    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان تحویل",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_shipments",
        verbose_name="ایجادکننده",
    )

    class Meta:
        verbose_name = "محموله"
        verbose_name_plural = "محموله‌ها"
        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return f"Shipment #{self.pk}"
