import uuid

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.cart.models import Cart, CartItem
from apps.cart.services.get_cart import get_cart, get_or_create_user_cart
from apps.products.models import Bundle, ProductVariant
from utils.exceptions import CartItemNotFound


def _variant_units_in_cart(
    cart,
    variant_id,
    *,
    exclude_item_id=None,
):
    """
    Sum stock units of a variant across variant lines and bundle lines.
    """
    qs = (
        CartItem.objects
        .filter(cart=cart)
        .filter(
            Q(variant_id=variant_id)
            | Q(bundle__variant_id=variant_id)
        )
        .select_related("bundle")
    )
    if exclude_item_id is not None:
        qs = qs.exclude(pk=exclude_item_id)

    used = 0
    for item in qs:
        if item.variant_id is not None:
            used += item.quantity
        else:
            used += item.quantity * item.bundle.quantity
    return used


def _raise_insufficient_stock(
    *,
    variant,
    required_total,
    is_bundle,
    bundle_quantity=1,
    other_units=0,
):
    if required_total <= variant.stock:
        return

    remaining = max(0, variant.stock - other_units)
    if is_bundle:
        raise ValidationError(
            {
                "detail": "Not enough stock for this bundle.",
                "available_quantity": (
                    remaining // bundle_quantity
                    if bundle_quantity
                    else 0
                ),
            }
        )

    raise ValidationError(
        {
            "detail": "Not enough stock.",
            "available_quantity": remaining,
        }
    )


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

    # ---------------------------------
    # Get / Create Cart
    # ---------------------------------

    if user and user.is_authenticated:

        cart, _ = get_or_create_user_cart(user)

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
    # Aggregate stock across variant + bundle lines
    # ---------------------------------

    existing_units = _variant_units_in_cart(
        cart,
        variant.id,
    )

    if variant_id is not None:
        additional_units = quantity
        is_bundle = False
        bundle_quantity = 1
    else:
        additional_units = quantity * bundle.quantity
        is_bundle = True
        bundle_quantity = bundle.quantity

    _raise_insufficient_stock(
        variant=variant,
        required_total=existing_units + additional_units,
        is_bundle=is_bundle,
        bundle_quantity=bundle_quantity,
        other_units=existing_units,
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

        other_units = _variant_units_in_cart(
            cart,
            item.variant_id,
            exclude_item_id=item.id,
        )
        required_total = other_units + quantity

        _raise_insufficient_stock(
            variant=item.variant,
            required_total=required_total,
            is_bundle=False,
            other_units=other_units,
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

        other_units = _variant_units_in_cart(
            cart,
            variant.id,
            exclude_item_id=item.id,
        )
        required_total = (
            other_units
            + quantity * item.bundle.quantity
        )

        _raise_insufficient_stock(
            variant=variant,
            required_total=required_total,
            is_bundle=True,
            bundle_quantity=item.bundle.quantity,
            other_units=other_units,
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
