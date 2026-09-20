from collections import defaultdict

from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from apps.orders.models import (
    OrderItem,
    OrderBundle,
)
from apps.products.models import ProductVariant


def calculate_cart(
    *,
    cart,
    order,
):
    """
    Calculates cart totals and prepares order items.

    Stock is calculated per ProductVariant across the entire cart.

    This is important because:
    - A normal variant consumes ProductVariant.stock directly.
    - A bundle also consumes the same ProductVariant.stock.
    - Therefore, normal items and bundles must be aggregated
      before checking stock.

    Returns:
        {
            "order_items": list[OrderItem],
            "order_bundles": list[OrderBundle],
            "products_total": int,
            "total_volume": int,
            "variants": list[(variant, quantity)],
        }
    """

    products_total = 0
    total_volume = 0

    order_items = []
    order_bundles = []
    variants = []

    cart_items = list(
        cart.items.select_related(
            "variant__product",
            "bundle__variant__product",
        )
    )

    # ---------------------------------------------------------
    # Collect all required stock per ProductVariant
    # ---------------------------------------------------------

    required_stock = defaultdict(int)

    for cart_item in cart_items:

        # -------------------------
        # Normal Variant
        # -------------------------
        if cart_item.variant:

            required_stock[
                cart_item.variant_id
            ] += cart_item.quantity

        # -------------------------
        # Bundle
        # -------------------------
        else:

            bundle = cart_item.bundle

            bundle_quantity = (
                bundle.quantity *
                cart_item.quantity
            )

            required_stock[
                bundle.variant_id
            ] += bundle_quantity

    # ---------------------------------------------------------
    # Lock all affected variants
    # ---------------------------------------------------------

    variant_ids = list(
        required_stock.keys()
    )

    locked_variants = {
        variant.id: variant
        for variant in (
            ProductVariant.objects
            .select_for_update()
            .select_related("product")
            .filter(id__in=variant_ids)
        )
    }

    # ---------------------------------------------------------
    # Make sure all variants still exist
    # ---------------------------------------------------------

    missing_variant_ids = (
        set(variant_ids)
        - set(locked_variants.keys())
    )

    if missing_variant_ids:
        raise ValidationError(
            _("One or more product variants do not exist.")
        )

    # ---------------------------------------------------------
    # Validate total stock
    # ---------------------------------------------------------

    for variant_id, quantity in required_stock.items():

        variant = locked_variants[variant_id]

        if quantity > variant.stock:
            raise ValidationError(
                _(
                    "Not enough stock for '%(product)s'."
                ) % {
                    "product": variant.product.title,
                }
            )

    # ---------------------------------------------------------
    # Prepare order items / bundles
    # ---------------------------------------------------------

    for cart_item in cart_items:

        # -------------------------
        # Variant
        # -------------------------
        if cart_item.variant:

            variant = locked_variants[
                cart_item.variant_id
            ]

            # قیمت اصلی محصول
            original_unit_price = variant.price

            # قیمت نهایی محصول بعد از تخفیف
            unit_price = (
                variant.discounted_price
                if variant.discounted_price is not None
                else variant.price
            )

            item_total = (
                unit_price *
                cart_item.quantity
            )

            order_items.append(
                OrderItem(
                    order=order,
                    variant=variant,
                    product_title=variant.product.title,
                    variant_sku=variant.sku,
                    quantity=cart_item.quantity,
                    original_unit_price=original_unit_price,
                    unit_price=unit_price,
                    total_price=item_total,
                    province=order.province,
                    city=order.city,
                    postal_code=order.postal_code,
                    full_address=order.address,
                )
            )

            products_total += item_total

            total_volume += (
                variant.volume *
                cart_item.quantity
            )

            variants.append(
                (
                    variant,
                    cart_item.quantity,
                )
            )

            continue

        # -------------------------
        # Bundle
        # -------------------------

        bundle = cart_item.bundle

        variant = locked_variants[
            bundle.variant_id
        ]

        bundle_quantity = (
            bundle.quantity *
            cart_item.quantity
        )

        bundle_total = (
            bundle.price *
            cart_item.quantity
        )

        order_bundle = OrderBundle(
            order=order,
            variant=variant,
            title=bundle.title,
            bundle_quantity=bundle.quantity,
            unit_price=bundle.price,
            quantity=cart_item.quantity,
            total_price=bundle_total,
        )

        order_bundles.append(
            order_bundle
        )

        variants.append(
            (
                variant,
                bundle_quantity,
            )
        )

        products_total += bundle_total

    return {
        "order_items": order_items,
        "order_bundles": order_bundles,
        "products_total": products_total,
        "total_volume": total_volume,
        "variants": variants,
    }