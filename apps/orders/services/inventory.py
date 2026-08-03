from apps.products.models import ProductVariant
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def reserve_stock(
        *,
        variants,
):
    """
    Decrease stock after creating an order.

    variants:
        [
            (variant, quantity),
            ...
        ]
    """

    updated_variants = []

    for variant, quantity in variants:
        if quantity <= 0:
            continue
        if variant.stock < quantity:
            raise ValidationError(
                _("Not enough stock.")
            )
        variant.stock -= quantity
        updated_variants.append(variant)

    ProductVariant.objects.bulk_update(
        updated_variants,
        ["stock"],
    )


def release_stock(
        *,
        variants,
):
    """
    Return stock after order expiration
    or payment rejection.

    variants:
        [
            (variant, quantity),
            ...
        ]
    """

    updated_variants = []

    for variant, quantity in variants:
        if quantity <= 0:
            continue
        if variant.stock < quantity:
            raise ValidationError(
                _("Not enough stock.")
            )
        variant.stock += quantity
        updated_variants.append(variant)

    ProductVariant.objects.bulk_update(
        updated_variants,
        ["stock"],
    )
