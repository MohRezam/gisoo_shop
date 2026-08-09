from apps.addresses.models import Address
from apps.shipping.models import ShippingMethod
from apps.cart.models import Cart, CartItem


def create_address(
        *,
        user,
):
    return Address.objects.create(
        user=user,
        full_name="Mohammadreza",
        phone_number="09123456789",
        province="Tehran",
        city="Tehran",
        address="Test Address",
        postal_code="1234567890",
    )


def create_shipping_method():
    return ShippingMethod.objects.create(
        title="Post",
        price=50000,
        estimated_days=3,
        is_active=True,
    )


def create_cart(
        *,
        user,
):
    return Cart.objects.create(
        user=user,
        is_active=True,
    )


def create_cart_item(
        *,
        cart,
        variant,
        quantity=1,
):
    return CartItem.objects.create(
        cart=cart,
        variant=variant,
        quantity=quantity,
    )
