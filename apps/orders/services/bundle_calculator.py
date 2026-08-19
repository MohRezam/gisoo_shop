from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from apps.orders.models import OrderItem
from apps.products.models import ProductVariant


def process_bundle(
    *,
    cart_item,
    order,
    order_bundle,
    order_items,
    variants,
):
    products_total = 0
    total_volume = 0

    for bundle_item in cart_item.bundle.items.select_related(
        "variant__product",
    ):

        variant = ProductVariant.objects.select_for_update().get(
            id=bundle_item.variant_id,
        )

        quantity = (
            bundle_item.quantity *
            cart_item.quantity
        )

        if quantity > variant.stock:
            raise ValidationError(
                _(
                    "Not enough stock for '%(product)s'."
                ) % {
                    "product": variant.product.title,
                }
            )

        item_total = (
            variant.price *
            quantity
        )

        order_items.append(
            OrderItem(
                order=order,
                order_bundle=order_bundle,
                variant=variant,
                product_title=variant.product.title,
                variant_sku=variant.sku,
                quantity=quantity,
                unit_price=variant.price,
                total_price=item_total,
            )
        )

        products_total += item_total

        total_volume += (
            variant.volume *
            quantity
        )

        variants.append(
            (
                variant,
                quantity,
            )
        )

    return {
        "products_total": products_total,
        "total_volume": total_volume,
    }