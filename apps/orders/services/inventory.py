from collections import defaultdict

from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from apps.products.models import ProductVariant


def _aggregate_variants(*, variants):
    """
    Aggregate quantities for the same ProductVariant.

    Example:

        [
            (variant, 3),
            (variant, 3),
            (variant, 2),
        ]

    becomes:

        {
            variant_id: 8,
        }
    """

    quantities = defaultdict(int)

    for variant, quantity in variants:
        if quantity <= 0:
            continue

        quantities[variant.id] += quantity

    return quantities


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

    The same ProductVariant may appear multiple times.
    Its quantities are aggregated before changing stock.

    The affected ProductVariant rows are locked with
    select_for_update() to prevent concurrent orders from
    consuming the same stock.
    """

    quantities = _aggregate_variants(
        variants=variants,
    )

    if not quantities:
        return

    variant_ids = list(quantities.keys())

    with transaction.atomic():
        locked_variants = list(
            ProductVariant.objects
            .select_for_update()
            .filter(id__in=variant_ids)
        )

        # Make sure all requested variants still exist.
        locked_variant_ids = {
            variant.id
            for variant in locked_variants
        }

        missing_variant_ids = (
            set(variant_ids) - locked_variant_ids
        )

        if missing_variant_ids:
            raise ValidationError(
                _("One or more product variants do not exist.")
            )

        # Validate ALL stock before changing ANY variant.
        # This prevents a partial inventory update.
        for variant in locked_variants:
            quantity = quantities[variant.id]

            if variant.stock < quantity:
                raise ValidationError(
                    _("Not enough stock.")
                )

        # All variants have enough stock.
        for variant in locked_variants:
            quantity = quantities[variant.id]
            variant.stock -= quantity

        ProductVariant.objects.bulk_update(
            locked_variants,
            ["stock"],
        )


def release_stock(
    *,
    variants,
):
    """
    Return reserved stock after order expiration
    or another operation that releases inventory.

    variants:
        [
            (variant, quantity),
            ...
        ]

    The same ProductVariant may appear multiple times.
    Its quantities are aggregated before changing stock.
    """

    quantities = _aggregate_variants(
        variants=variants,
    )

    if not quantities:
        return

    variant_ids = list(quantities.keys())

    with transaction.atomic():
        locked_variants = list(
            ProductVariant.objects
            .select_for_update()
            .filter(id__in=variant_ids)
        )

        # Make sure all requested variants still exist.
        locked_variant_ids = {
            variant.id
            for variant in locked_variants
        }

        missing_variant_ids = (
            set(variant_ids) - locked_variant_ids
        )

        if missing_variant_ids:
            raise ValidationError(
                _("One or more product variants do not exist.")
            )

        for variant in locked_variants:
            quantity = quantities[variant.id]
            variant.stock += quantity

        ProductVariant.objects.bulk_update(
            locked_variants,
            ["stock"],
        )
