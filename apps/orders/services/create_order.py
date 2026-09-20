from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from apps.addresses.models import Address
from apps.cart.models import Cart
from apps.notifications.services.inbox import notify_user
from apps.orders.constants import ORDER_EXPIRATION_MINUTES
from apps.orders.models import (
    Order,
    OrderItem,
    OrderStatus,
    OrderBundle,
)
from apps.orders.services.cart_calculator import calculate_cart
from apps.orders.services.expiration import schedule_order_expiration
from apps.orders.services.inventory import reserve_stock
from apps.orders.services.public_number import generate_order_public_number
from apps.payments.services.create_payment import create_payment
from apps.payments.services.create_payment_intent import create_payment_intent
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
        status=OrderStatus.WAITING_PAYMENT,
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

    order.public_number = generate_order_public_number(order.id)
    order.save(update_fields=["public_number"])

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

    products_total = cart_result["products_total"]

    discount = None
    discount_amount = 0

    if cart.discount_id is not None:
        try:
            discount_result = calculate_discount(
                user=user,
                code=cart.discount.code,
                products_price=products_total,
            )

            discount = discount_result["discount"]
            discount_amount = discount_result["discount_amount"]

        except ValidationError:
            cart.discount = None
            cart.save(
                update_fields=["discount"]
            )

            discount = None
            discount_amount = 0

    order.products_price = products_total
    order.shipping_price = shipping_price
    order.discount = discount
    order.discount_amount = discount_amount
    order.total_price = (
            products_total
            + shipping_price
            - discount_amount
    )

    order.save(
        update_fields=[
            "products_price",
            "shipping_price",
            "discount",
            "discount_amount",
            "total_price",
        ]
    )

    OrderBundle.objects.bulk_create(
        cart_result["order_bundles"],
    )

    OrderItem.objects.bulk_create(
        cart_result["order_items"]
    )

    # Legacy gateway payment row (optional / unused by shop C2C UI)
    create_payment(order=order)

    # Primary shop flow: C2C payment intent
    create_payment_intent(order=order, user=user)

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

    notify_user(
        user=user,
        title="سفارش ثبت شد",
        body=f"سفارش {order.public_number} ثبت شد. لطفاً پرداخت کارت‌به‌کارت را انجام دهید.",
        type="order",
        link=f"/account/orders/{order.id}",
        order_id=order.id,
    )

    return (
        Order.objects.select_related("shipping_method", "payment")
        .prefetch_related("payment_intents__destination_card")
        .get(pk=order.pk)
    )
