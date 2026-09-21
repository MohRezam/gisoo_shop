from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shared.models.base import BaseModel
from apps.shipping.models import ShippingCarrier, ShippingMethod
from apps.users.models import User
from apps.products.models import ProductVariant


class OrderStatus(models.TextChoices):
    WAITING_PAYMENT = (
        "waiting_payment",
        "در انتظار پرداخت",
    )

    PAYMENT_REJECTED = (
        "payment_rejected",
        "پرداخت رد شده",
    )

    PREPARING = (
        "preparing",
        "در حال آماده‌سازی",
    )

    SHIPPED = (
        "shipped",
        "ارسال شده",
    )

    DELIVERED = (
        "delivered",
        "تحویل شده",
    )

    CANCELED = (
        "canceled",
        "لغو شده",
    )

    EXPIRED = (
        "expired",
        "منقضی شده",
    )


class Order(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="کاربر",
    )

    public_number = models.CharField(
        max_length=32,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="شماره عمومی",
    )

    phone_number = models.CharField(
        max_length=11,
        verbose_name="شماره تلفن",
    )

    status = models.CharField(
        max_length=30,
        choices=OrderStatus.choices,
        default=OrderStatus.WAITING_PAYMENT,
        verbose_name="وضعیت",
    )

    tracking_code = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="کد پیگیری",
    )

    carrier = models.CharField(
        max_length=16,
        choices=ShippingCarrier.choices,
        blank=True,
        default="",
        verbose_name="حامل",
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ انقضا",
    )
    prepared_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان آماده‌سازی",
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

    province = models.CharField(
        max_length=255,
        verbose_name="استان",
    )

    city = models.CharField(
        max_length=255,
        verbose_name="شهر",
    )
    postal_code = models.CharField(
        max_length=20,
        verbose_name="کد پستی",
    )

    address = models.TextField(
        verbose_name="آدرس",
    )
    shipping_method = models.ForeignKey(
        ShippingMethod,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="روش ارسال",
    )

    products_price = models.PositiveBigIntegerField(
        verbose_name="قیمت محصولات",
        default=0,
    )

    shipping_price = models.PositiveBigIntegerField(
        verbose_name="هزینه ارسال",
        default=0,
    )

    discount = models.ForeignKey(
        "discounts.Discount",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="تخفیف",
    )
    discount_amount = models.PositiveBigIntegerField(
        verbose_name="مبلغ تخفیف",
        default=0,
    )

    total_price = models.PositiveBigIntegerField(
        default=0,
        verbose_name="مبلغ کل",
    )

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"


class OrderBundle(BaseModel):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="bundles",
        verbose_name="سفارش",
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name="order_bundles",
        verbose_name=_("variant"),
    )

    title = models.CharField(
        max_length=255,
        verbose_name="عنوان",
    )

    bundle_quantity = models.PositiveIntegerField(
        verbose_name=_("bundle quantity"),
    )

    unit_price = models.PositiveBigIntegerField(
        verbose_name="قیمت واحد",
    )

    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="تعداد",
    )

    total_price = models.PositiveBigIntegerField(
        verbose_name="مبلغ کل",
    )

    class Meta:
        verbose_name = "بسته سفارش"
        verbose_name_plural = "بسته‌های سفارش"

    def __str__(self):
        return self.title


class OrderItem(BaseModel):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="سفارش",
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        verbose_name="تنوع محصول",
    )

    order_bundle = models.ForeignKey(
        "orders.OrderBundle",
        on_delete=models.CASCADE,
        related_name="items",
        null=True,
        blank=True,
        verbose_name="بسته سفارش",
    )

    product_title = models.CharField(
        max_length=255,
        verbose_name="عنوان محصول",
    )

    variant_sku = models.CharField(
        max_length=100,
        verbose_name="کد کالا",
    )

    quantity = models.PositiveIntegerField(
        verbose_name="تعداد",
    )

    original_unit_price = models.PositiveIntegerField(
        verbose_name="قیمت واحد اصلی",
    )

    unit_price = models.PositiveIntegerField(
        verbose_name="قیمت واحد",
    )

    total_price = models.PositiveIntegerField(
        verbose_name="مبلغ کل",
    )

    province = models.CharField(
        max_length=100,
        verbose_name="استان",
    )

    city = models.CharField(
        max_length=100,
        verbose_name="شهر",
    )

    postal_code = models.CharField(
        max_length=20,
        verbose_name="کد پستی",
    )

    full_address = models.TextField(
        verbose_name="آدرس کامل",
    )

    class Meta:
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"


class OrderStatusHistory(BaseModel):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="status_history",
        verbose_name="سفارش",
    )

    old_status = models.CharField(
        max_length=30,
        choices=OrderStatus.choices,
        verbose_name="وضعیت قبلی",
    )

    new_status = models.CharField(
        max_length=30,
        choices=OrderStatus.choices,
        verbose_name="وضعیت جدید",
    )

    changed_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="changed_order_statuses",
        verbose_name="تغییردهنده",
    )

    reason = models.TextField(
        blank=True,
        verbose_name="دلیل",
    )
    source = models.CharField(
        max_length=30,
        choices=[
            ("admin", "Admin"),
            ("system", "System"),
            ("customer", "Customer"),
        ],
        default="system",
        verbose_name="منبع",
    )

    class Meta:
        verbose_name = "تاریخچه وضعیت سفارش"
        verbose_name_plural = "تاریخچه‌های وضعیت سفارش"
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Order #{self.order_id}: "
            f"{self.old_status} → {self.new_status}"
        )
