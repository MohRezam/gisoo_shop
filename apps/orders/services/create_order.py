from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from apps.addresses.models import Address
from apps.cart.models import Cart
from apps.cart.services.pricing import (
    get_bundle_prices,
    get_variant_prices,
)
from apps.discounts.services import calculate_discount
from apps.notifications.services.inbox import notify_user
from apps.notifications.tasks import send_order_created_sms
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

    # Lock the active cart so concurrent checkouts cannot both
    # create an order from the same cart.
    cart = (
        Cart.objects
        .select_for_update()
        .filter(
            user=user,
            is_active=True,
        )
        .first()
    )

    if cart is None:
        raise ValidationError(
            _("Cart not found or is no longer available.")
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
        carrier=shipping_method.carrier,
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
        cart_discount = cart.discount
        eligible_price = products_total

        if not cart_discount.applies_to_discounted_products:
            eligible_price = 0
            for item in cart.items.select_related(
                "variant",
                "bundle",
                "bundle__variant",
            ):
                if item.variant_id:
                    prices = get_variant_prices(item.variant)
                    if not prices["is_discounted"]:
                        eligible_price += (
                            prices["unit_price"]
                            * item.quantity
                        )
                elif item.bundle_id:
                    prices = get_bundle_prices(item.bundle)
                    if not prices["is_discounted"]:
                        eligible_price += (
                            prices["unit_price"]
                            * item.quantity
                        )

        try:
            # Lock discount row and re-validate limits, counting
            # other WAITING_PAYMENT orders as soft reservations.
            discount_result = calculate_discount(
                user=user,
                code=cart_discount.code,
                products_price=products_total,
                eligible_price=eligible_price,
                for_update=True,
                include_pending_reservations=True,
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

    create_payment_intent(order_id=order.id, user=user)

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

    order_id = order.id
    public_number = order.public_number
    phone = order.phone_number
    amount = order.total_price
    user_id = user.id

    def _notify_order_created():
        notify_user(
            user=user,
            title="سفارش ثبت شد",
            body=(
                f"سفارش {public_number} ثبت شد. "
                "لطفاً پرداخت کارت‌به‌کارت را انجام دهید."
            ),
            type="order",
            link=f"/account/orders/{order_id}",
            order_id=order_id,
        )
        send_order_created_sms.delay(
            user_id=user_id,
            recipient=phone,
            order_id=order_id,
            amount=amount,
        )
        try:
            from apps.notifications.models import AdminAlertType
            from apps.notifications.services.admin_alerts import notify_admin

            notify_admin(
                title="سفارش جدید",
                body=f"سفارش {public_number} ثبت شد.",
                type=AdminAlertType.ORDER,
                link=f"/admin/orders/order/{order_id}/change/",
            )
        except Exception:
            pass

    transaction.on_commit(_notify_order_created)

    return order
