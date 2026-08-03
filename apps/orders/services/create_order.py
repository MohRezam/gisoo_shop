from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from apps.addresses.models import Address
from apps.cart.models import Cart
from apps.orders.constants import ORDER_EXPIRATION_MINUTES
from apps.orders.models import (
    Order,
    OrderItem,
    OrderStatus, OrderBundle,
)
from apps.orders.services.cart_calculator import calculate_cart
from apps.orders.services.expiration import schedule_order_expiration
from apps.orders.services.inventory import reserve_stock
from apps.payments.services.create_payment import create_payment
from apps.shipping.models import ShippingMethod
from apps.shipping.services.shipping import calculate_shipping_price


@transaction.atomic
def create_order(
        *,
        user,
        address_id,
        shipping_method_id,
        description="",
):
    address = Address.objects.filter(
        id=address_id,
        user=user,
    ).first()

    if address is None:
        raise ValidationError(
            _("Address not found.")
        )

    shipping_method = ShippingMethod.objects.filter(
        id=shipping_method_id,
        is_active=True,
    ).first()

    if shipping_method is None:
        raise ValidationError(
            _("Invalid shipping method.")
        )

    cart = (
        Cart.objects
        .prefetch_related(
            "items__variant__product",
        )
        .filter(
            user=user,
            is_active=True,
        )
        .first()
    )

    if cart is None:
        raise ValidationError(
            _("Cart not found.")
        )

    if not cart.items.exists():
        raise ValidationError(
            _("Cart is empty.")
        )

    order = Order.objects.create(
        user=user,
        status=OrderStatus.CREATED,
        expires_at=timezone.now() + timedelta(
            minutes=ORDER_EXPIRATION_MINUTES,
        ),
        description=description,
        phone_number=address.phone_number,
        province=address.province,
        city=address.city,
        postal_code=address.postal_code,
        address=address.address,
        shipping_method=shipping_method,
    )

    cart_result = calculate_cart(
        cart=cart,
        order=order,
    )

    reserve_stock(
        variants=cart_result["variants"],
    )

    shipping_price = calculate_shipping_price(
        shipping_method=shipping_method,
        products_total=cart_result["products_total"],
    )

    order.products_price = cart_result["products_total"]
    order.shipping_price = shipping_price
    order.total_price = (
            cart_result["products_total"]
            + shipping_price
    )

    order.save(
        update_fields=[
            "products_price",
            "shipping_price",
            "total_price",
        ]
    )

    OrderBundle.objects.bulk_create(
        cart_result["order_bundles"],
    )

    OrderItem.objects.bulk_create(
        cart_result["order_items"]
    )

    create_payment(
        order=order,
    )

    cart.is_active = False
    cart.save(
        update_fields=[
            "is_active",
        ]
    )

    cart.items.all().delete()

    schedule_order_expiration(
        order=order,
    )

    return order
