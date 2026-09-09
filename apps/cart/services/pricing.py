from apps.cart.models import Cart
from apps.discounts.models import Discount
from apps.discounts.services import calculate_discount


def get_variant_prices(variant):
    """
    Return original and current prices for a product variant.
    """

    original_price = variant.price

    current_price = (
        variant.discounted_price
        if variant.discounted_price is not None
        else variant.price
    )

    product_discount = (
            original_price - current_price
    )

    return {
        "original_unit_price": original_price,
        "unit_price": current_price,
        "product_discount_unit": product_discount,
        "is_discounted": (
                variant.discounted_price is not None
        ),
    }


def get_bundle_prices(bundle):
    """
    Return original and current prices for a bundle.
    """

    original_price = (
            bundle.variant.price
            * bundle.quantity
    )

    current_price = bundle.price

    bundle_discount = max(
        0,
        original_price - current_price,
    )

    return {
        "original_unit_price": original_price,
        "unit_price": current_price,
        "discount_unit": bundle_discount,
        "is_discounted": (
                current_price < original_price
        ),
    }


def calculate_cart_totals(
        cart: Cart,
        user=None,
        discount: Discount | None = None,
):
    """
    Calculate cart totals.

    Product/bundle discounts are applied first.
    Coupon discount is applied afterwards.
    """

    original_subtotal = 0
    product_discount = 0
    coupon_eligible_price = 0

    items = (
        cart.items
        .select_related(
            "variant",
            "variant__product",
            "bundle",
            "bundle__variant",
            "bundle__variant__product",
        )
    )

    for item in items:

        if item.variant_id:
            prices = get_variant_prices(
                item.variant
            )

            item_original_total = (
                    prices["original_unit_price"]
                    * item.quantity
            )

            item_discount = (
                    prices["product_discount_unit"]
                    * item.quantity
            )

            item_current_total = (
                    prices["unit_price"]
                    * item.quantity
            )

            original_subtotal += item_original_total
            product_discount += item_discount

            if (
                    discount is None
                    or discount.applies_to_discounted_products
                    or not prices["is_discounted"]
            ):
                coupon_eligible_price += (
                    item_current_total
                )

        elif item.bundle_id:
            prices = get_bundle_prices(
                item.bundle
            )

            item_original_total = (
                    prices["original_unit_price"]
                    * item.quantity
            )

            item_discount = (
                    prices["discount_unit"]
                    * item.quantity
            )

            item_current_total = (
                    prices["unit_price"]
                    * item.quantity
            )

            original_subtotal += item_original_total
            product_discount += item_discount

            if (
                    discount is None
                    or discount.applies_to_discounted_products
                    or not prices["is_discounted"]
            ):
                coupon_eligible_price += (
                    item_current_total
                )

    subtotal = (
            original_subtotal
            - product_discount
    )

    coupon_discount = 0

    if discount is not None:
        result = calculate_discount(
            user=user,
            code=discount.code,
            products_price=subtotal,
            eligible_price=coupon_eligible_price,
        )

        coupon_discount = result["discount_amount"]

    total = subtotal - coupon_discount

    return {
        "original_subtotal": original_subtotal,
        "product_discount": product_discount,
        "subtotal": subtotal,
        "coupon_discount": coupon_discount,
        "total": total,
        "discount": discount,
    }
