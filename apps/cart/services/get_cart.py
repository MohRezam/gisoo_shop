from django.shortcuts import get_object_or_404

from apps.cart.models import Cart


def get_cart(
    *,
    user,
    cart_uuid: str | None,
):
    if user and user.is_authenticated:
        return get_object_or_404(
            Cart,
            user=user,
            is_active=True,
        )

    if not cart_uuid:
        return None

    return get_object_or_404(
        Cart,
        uuid=cart_uuid,
        is_active=True,
    )