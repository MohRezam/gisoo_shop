from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shared.models.base import BaseModel
from apps.shipping.models import ShippingMethod
from apps.users.models import User
from apps.products.models import ProductVariant


class OrderStatus(models.TextChoices):
    CREATED = (
        "created",
        _("Created"),
    )

    PREPARING = (
        "preparing",
        _("Preparing"),
    )

    SHIPPED = (
        "shipped",
        _("Shipped"),
    )

    DELIVERED = (
        "delivered",
        _("Delivered"),
    )

    CANCELED = (
        "canceled",
        _("Canceled"),
    )

    EXPIRED = (
        "expired",
        _("Expired"),
    )


class Order(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name=_("user"),
    )

    phone_number = models.CharField(
        max_length=11,
        verbose_name=_("phone number"),
    )

    status = models.CharField(
        max_length=30,
        choices=OrderStatus.choices,
        default=OrderStatus.CREATED,
        verbose_name=_("status"),
    )

    description = models.TextField(
        blank=True,
        verbose_name=_("description"),
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    prepared_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("prepared at"),
    )

    shipped_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("shipped at"),
    )

    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("delivered at"),
    )

    province = models.CharField(
        max_length=255
    )

    city = models.CharField(
        max_length=255
    )
    postal_code = models.CharField(
        max_length=20,
        verbose_name=_("postal code"),
    )

    address = models.TextField(
        verbose_name=_("address"),
    )
    shipping_method = models.ForeignKey(
        ShippingMethod,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name=_("Shipping method"),
    )

    products_price = models.PositiveBigIntegerField(
        verbose_name=_("Products price"),
        default=0,
    )

    shipping_price = models.PositiveBigIntegerField(
        verbose_name=_("Shipping price"),
        default=0,
    )

    discount = models.ForeignKey(
        "discounts.Discount",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name=_("Discount"),
    )
    discount_amount = models.PositiveBigIntegerField(
        verbose_name=_("Discount amount"),
        default=0,
    )

    total_price = models.PositiveBigIntegerField(
        default=0,
        verbose_name=_("total price"),
    )

    class Meta:
        verbose_name = _("order")
        verbose_name_plural = _("orders")


class OrderBundle(BaseModel):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="bundles",
        verbose_name=_("order"),
    )

    title = models.CharField(
        max_length=255,
        verbose_name=_("title"),
    )

    unit_price = models.PositiveBigIntegerField(
        verbose_name=_("unit_price"),
    )

    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name=_("quantity"),
    )

    total_price = models.PositiveBigIntegerField(
        verbose_name=_("total_price"),
    )

    class Meta:
        verbose_name = _("order bundle")
        verbose_name_plural = _("order bundles")

    def __str__(self):
        return self.title


class OrderItem(BaseModel):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
    )

    order_bundle = models.ForeignKey(
        "orders.OrderBundle",
        on_delete=models.CASCADE,
        related_name="items",
        null=True,
        blank=True,
    )

    product_title = models.CharField(
        max_length=255,
    )

    variant_sku = models.CharField(
        max_length=100,
    )

    quantity = models.PositiveIntegerField()

    unit_price = models.PositiveIntegerField()

    total_price = models.PositiveIntegerField()

    province = models.CharField(max_length=100)

    city = models.CharField(max_length=100)

    postal_code = models.CharField(max_length=20)

    full_address = models.TextField()


class OrderStatusHistory(BaseModel):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="status_history",
    )

    old_status = models.CharField(
        max_length=30,
        choices=OrderStatus.choices,
    )

    new_status = models.CharField(
        max_length=30,
        choices=OrderStatus.choices,
    )

    changed_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="changed_order_statuses",
    )

    reason = models.TextField(
        blank=True,
    )
    source = models.CharField(
        max_length=30,
        choices=[
            ("admin", "Admin"),
            ("system", "System"),
            ("customer", "Customer"),
        ],
        default="system",
    )

    class Meta:
        verbose_name = _("order status history")
        verbose_name_plural = _("order status histories")
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Order #{self.order_id}: "
            f"{self.old_status} → {self.new_status}"
        )
