from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.cart.models import Cart
from apps.cart.services.pricing import calculate_cart_totals
from apps.discounts.models import Discount


@transaction.atomic
def apply_discount_to_cart(
    *,
    cart: Cart,
    user,
    code: str,
):
    code = code.strip().upper()

    if not code:
        raise ValidationError(
            "Discount code is required."
        )

    discount = Discount.objects.filter(
        code=code,
    ).first()

    if discount is None:
        raise ValidationError(
            "Discount code not found."
        )

    # Validate the new code first. Do not assign yet — if validation
    # fails, the cart keeps any previously applied coupon.
    result = calculate_cart_totals(
        cart=cart,
        user=user,
        discount=discount,
        raise_on_invalid=True,
    )

    cart.discount = discount

    cart.save(
        update_fields=[
            "discount",
        ]
    )

    return result


@transaction.atomic
def remove_discount_from_cart(
    *,
    cart: Cart,
    user,
):
    cart.discount = None

    cart.save(
        update_fields=[
            "discount",
        ]
    )

    return calculate_cart_totals(
        cart=cart,
        user=user,
    )
