from django.db import IntegrityError, transaction
from django.http import Http404
from django.shortcuts import get_object_or_404

from apps.cart.models import Cart


def ensure_single_active_user_cart(user):
    """
    Return the user's newest active cart, deactivating any extras.
    """
    carts = list(
        Cart.objects.filter(
            user=user,
            is_active=True,
        ).order_by("-id")
    )
    if not carts:
        return None

    cart = carts[0]
    if len(carts) > 1:
        Cart.objects.filter(
            user=user,
            is_active=True,
        ).exclude(
            pk=cart.pk,
        ).update(
            is_active=False,
        )
    return cart


def get_or_create_user_cart(user):
    cart = ensure_single_active_user_cart(user)
    if cart is not None:
        return cart, False

    try:
        with transaction.atomic():
            cart = Cart.objects.create(
                user=user,
                is_active=True,
            )
        return cart, True
    except IntegrityError:
        cart = ensure_single_active_user_cart(user)
        if cart is None:
            raise
        return cart, False


def get_cart(
    *,
    user,
    cart_uuid: str | None,
):
    if user and user.is_authenticated:
        # Always resolve by ownership. Never accept cart_uuid for
        # authenticated users (prevents mutating another user's cart).
        cart = ensure_single_active_user_cart(user)
        if cart is None:
            raise Http404
        return cart

    if not cart_uuid:
        return None

    return get_object_or_404(
        Cart,
        uuid=cart_uuid,
        user__isnull=True,
        is_active=True,
    )
