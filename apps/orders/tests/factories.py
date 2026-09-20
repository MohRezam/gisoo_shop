from apps.addresses.tests.factories import create_address  # noqa: F401
from apps.cart.tests.factories import create_cart, create_cart_item  # noqa: F401
from apps.shipping.models import ShippingMethod


def create_shipping_method(**overrides):
    data = {
        "title": overrides.pop("title", "Post"),
        "price": 50000,
        "free_shipping_minimum": 0,
        "estimated_days": 3,
        "is_active": True,
    }
    data.update(overrides)
    return ShippingMethod.objects.create(**data)
