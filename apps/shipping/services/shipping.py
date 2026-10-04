from apps.shipping.models import ShippingMethod


def calculate_shipping_price(
    *,
    shipping_method: ShippingMethod,
    products_total,
):
    # free_shipping_minimum=0 means no free-shipping threshold.
    minimum = shipping_method.free_shipping_minimum
    if minimum > 0 and products_total >= minimum:
        return 0

    return shipping_method.price
