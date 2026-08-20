from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from apps.orders.models import OrderBundle, OrderItem
from apps.products.models import ProductVariant


def calculate_cart(
    *,
    cart,
    order,
):
    """
    Calculates cart totals and prepares order items.

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

    cart_items = cart.items.select_related(
        "variant__product",
        "bundle",
    )

    for cart_item in cart_items:

        # -------------------------
        # Variant
        # -------------------------
        if cart_item.variant:

            variant = ProductVariant.objects.select_for_update().get(
                pk=cart_item.variant_id,
            )

            if cart_item.quantity > variant.stock:
                raise ValidationError(
                    _(
                        "Not enough stock for '%(product)s'."
                    ) % {
                        "product": variant.product.title,
                    }
                )

            item_total = (
                variant.price *
                cart_item.quantity
            )

            order_items.append(
                OrderItem(
                    order=order,
                    variant=variant,
                    product_title=variant.product.title,
                    variant_sku=variant.sku,
                    quantity=cart_item.quantity,
                    unit_price=variant.price,
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

        bundle_total = (
            bundle.price *
            cart_item.quantity
        )

        order_bundle = OrderBundle(
            order=order,
            bundle=bundle,
            title=bundle.title,
            unit_price=bundle.price,
            quantity=cart_item.quantity,
            total_price=bundle_total,
        )

        order_bundles.append(order_bundle)

        products_total += bundle_total

    return {
        "order_items": order_items,
        "order_bundles": order_bundles,
        "products_total": products_total,
        "total_volume": total_volume,
        "variants": variants,
    }