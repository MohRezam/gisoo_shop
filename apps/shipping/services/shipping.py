from apps.shipping.models import ShippingMethod


def calculate_shipping_price(
    *,
    shipping_method: ShippingMethod,
    products_total,
):
    if (
        products_total >=
        shipping_method.free_shipping_minimum
    ):
        return 0

    return shipping_method.price