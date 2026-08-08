import uuid

from apps.cart.models import Cart, CartItem
from apps.cart.services.get_cart import get_cart
from apps.products.models import ProductVariant
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from utils.exceptions import CartItemNotFound


def add_to_cart(
        *,
        cart_uuid: str | None,
        user,
        variant_id: int,
        quantity: int,
):
    variant = get_object_or_404(
        ProductVariant,
        id=variant_id,
        is_active=True,
    )

    if quantity > variant.stock:
        raise ValidationError(
            "Not enough stock."
        )

    if user and user.is_authenticated:
        if quantity > variant.stock:
            raise ValidationError(
                "Not enough stock."
            )
        cart, _ = Cart.objects.get_or_create(
            user=user,
            is_active=True,
        )

    else:
        if cart_uuid:
            if quantity > variant.stock:
                raise ValidationError(
                    "Not enough stock."
                )
            cart, _ = Cart.objects.get_or_create(
                uuid=cart_uuid,
                defaults={
                    "is_active": True,
                },
            )
        else:
            cart = Cart.objects.create(
                uuid=uuid.uuid4(),
            )

    if quantity > variant.stock:
        raise ValidationError(
            "Not enough stock."
        )
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        variant=variant,
        defaults={
            "quantity": quantity,
        },
    )

    if not created:
        new_quantity = cart_item.quantity + quantity

        if new_quantity > variant.stock:
            raise ValidationError(
                "Not enough stock."
            )

        cart_item.quantity = new_quantity

        cart_item.save(
            update_fields=[
                "quantity",
            ]
        )

    return cart


def update_cart_item(
        *,
        user,
        cart_uuid,
        item_id,
        quantity,
):
    try:
        cart = get_cart(
            user=user,
            cart_uuid=cart_uuid,
        )

        item = CartItem.objects.select_related(
            "variant",
        ).get(
            id=item_id,
            cart=cart,
        )

    except CartItem.DoesNotExist:
        raise CartItemNotFound()

    if quantity > item.variant.stock:
        raise ValidationError(
            "Not enough stock."
        )

    item.quantity = quantity
    item.save(
        update_fields=["quantity"]
    )

    return item


def delete_cart_item(
        *,
        user,
        cart_uuid,
        item_id,
):
    try:
        cart = get_cart(
            user=user,
            cart_uuid=cart_uuid,
        )

        item = CartItem.objects.get(
            id=item_id,
            cart=cart,
        )

    except CartItem.DoesNotExist:
        raise CartItemNotFound()

    item.delete()
