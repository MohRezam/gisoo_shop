import uuid

from apps.cart.models import Cart, CartItem
from apps.products.models import ProductVariant, Bundle
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from utils.exceptions import CartItemNotFound
from apps.cart.services.get_cart import get_cart


def add_to_cart(
        *,
        cart_uuid: str | None,
        user,
        variant_id: int | None = None,
        bundle_id: int | None = None,
        quantity: int = 1,
):
    if (variant_id is None) == (bundle_id is None):
        raise ValidationError(
            "Provide either variant_id or bundle_id."
        )

    if quantity < 1:
        raise ValidationError(
            "Quantity must be greater than zero."
        )

    # ---------------------------------
    # Validate Variant / Bundle
    # ---------------------------------

    if variant_id is not None:

        variant = get_object_or_404(
            ProductVariant,
            id=variant_id,
            is_active=True,
        )

        bundle = None

        required_stock = quantity

        if required_stock > variant.stock:
            raise ValidationError(
                {
                    "detail": "Not enough stock.",
                    "available_quantity": variant.stock,
                }
            )

    else:

        bundle = get_object_or_404(
            Bundle.objects.select_related(
                "variant",
            ),
            id=bundle_id,
            is_active=True,
        )

        variant = bundle.variant

        if not variant.is_active:
            raise ValidationError(
                "The product variant of this bundle is not active."
            )

        required_stock = (
            quantity * bundle.quantity
        )

        if required_stock > variant.stock:
            raise ValidationError(
                {
                    "detail": "Not enough stock for this bundle.",
                    "available_quantity": (
                        variant.stock // bundle.quantity
                    ),
                }
            )

    # ---------------------------------
    # Get / Create Cart
    # ---------------------------------

    if user and user.is_authenticated:

        cart, _ = Cart.objects.get_or_create(
            user=user,
            is_active=True,
        )

    else:

        if cart_uuid:

            # فقط Guest Cart مجاز است.
            cart = (
                Cart.objects
                .filter(
                    uuid=cart_uuid,
                    user__isnull=True,
                    is_active=True,
                )
                .first()
            )

            if cart is None:
                raise ValidationError(
                    "Invalid cart."
                )

        else:

            cart = Cart.objects.create(
                uuid=uuid.uuid4(),
                is_active=True,
            )

    # ---------------------------------
    # Add Variant
    # ---------------------------------

    if variant_id is not None:

        cart_item, created = (
            CartItem.objects.get_or_create(
                cart=cart,
                variant=variant,
                bundle=None,
                defaults={
                    "quantity": quantity,
                },
            )
        )

    # ---------------------------------
    # Add Bundle
    # ---------------------------------

    else:

        cart_item, created = (
            CartItem.objects.get_or_create(
                cart=cart,
                bundle=bundle,
                variant=None,
                defaults={
                    "quantity": quantity,
                },
            )
        )

    # ---------------------------------
    # Existing Item
    # ---------------------------------

    if not created:

        new_quantity = (
            cart_item.quantity + quantity
        )

        if variant_id is not None:

            required_stock = new_quantity

        else:

            required_stock = (
                new_quantity * bundle.quantity
            )

        if required_stock > variant.stock:

            if variant_id is not None:

                raise ValidationError(
                    {
                        "detail": "Not enough stock.",
                        "available_quantity": variant.stock,
                    }
                )

            available_quantity = (
                variant.stock // bundle.quantity
            )

            raise ValidationError(
                {
                    "detail": "Not enough stock for this bundle.",
                    "available_quantity": available_quantity,
                }
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
            "bundle__variant",
        ).get(
            id=item_id,
            cart=cart,
        )

    except CartItem.DoesNotExist:
        raise CartItemNotFound()

    # -----------------------------------------
    # Validate quantity
    # -----------------------------------------

    if quantity < 1:
        raise ValidationError(
            "Quantity must be greater than zero."
        )

    # -----------------------------------------
    # PRODUCT
    # -----------------------------------------

    if item.variant is not None:

        required_stock = quantity

        if required_stock > item.variant.stock:
            raise ValidationError(
                {
                    "detail": "Not enough stock.",
                    "available_quantity": item.variant.stock,
                }
            )

    # -----------------------------------------
    # BUNDLE
    # -----------------------------------------

    elif item.bundle is not None:

        variant = item.bundle.variant

        if not variant.is_active:
            raise ValidationError(
                "The product variant of this bundle is not active."
            )

        # Each bundle consumes `bundle.quantity`
        # units of the variant.
        required_stock = (
            quantity * item.bundle.quantity
        )

        if required_stock > variant.stock:

            available_quantity = (
                variant.stock // item.bundle.quantity
            )

            raise ValidationError(
                {
                    "detail": "Not enough stock for this bundle.",
                    "available_quantity": available_quantity,
                }
            )

    # -----------------------------------------
    # INVALID CART ITEM
    # -----------------------------------------

    else:
        raise ValidationError(
            "Invalid cart item."
        )

    # -----------------------------------------
    # UPDATE
    # -----------------------------------------

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