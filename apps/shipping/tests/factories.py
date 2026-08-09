from apps.shipping.models import ShippingMethod


def create_shipping_method():
    return ShippingMethod.objects.create(
        title="Post",
        price=50000,
        estimated_days=3,
        is_active=True,
    )