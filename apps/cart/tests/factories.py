from apps.cart.models import Cart, CartItem


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