from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.addresses.tests.factories import create_address
from apps.cart.tests.factories import (
    create_cart,
    create_cart_item,
)
from apps.orders.models import Order, OrderStatus
from apps.orders.services.cart_calculator import calculate_cart
from apps.orders.tests.factories import create_shipping_method
from apps.products.tests.factories import (
    create_brand,
    create_category,
    create_product,
    create_product_variant,
)

User = get_user_model()


class CalculateCartTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            phone_number="09120000000",
        )

        self.address = create_address(
            user=self.user,
        )

        self.shipping = create_shipping_method()

        self.cart = create_cart(
            user=self.user,
        )

        category = create_category(
            slug="cat-1",
        )

        brand = create_brand(
            slug="brand-1",
        )

        product = create_product(
            category=category,
            brand=brand,
            slug="product-1",
        )

        self.variant = create_product_variant(
            product=product,
            sku="sku-1",
            price=100000,
        )

        self.order = Order.objects.create(
            user=self.user,
            phone_number=self.address.phone_number,
            province=self.address.province,
            city=self.address.city,
            postal_code=self.address.postal_code,
            address=self.address.address,
            shipping_method=self.shipping,
            status=OrderStatus.CREATED,
        )

    def test_calculate_cart_success(self):
        create_cart_item(
            cart=self.cart,
            variant=self.variant,
            quantity=2,
        )

        result = calculate_cart(
            cart=self.cart,
            order=self.order,
        )

        self.assertEqual(
            result["products_total"],
            200000,
        )

        self.assertEqual(
            result["total_volume"],
            self.variant.volume * 2,
        )

        self.assertEqual(
            len(result["order_items"]),
            1,
        )

        self.assertEqual(
            len(result["variants"]),
            1,
        )

    def test_not_enough_stock(self):
        self.variant.stock = 1
        self.variant.save()

        create_cart_item(
            cart=self.cart,
            variant=self.variant,
            quantity=2,
        )

        with self.assertRaises(ValidationError):
            calculate_cart(
                cart=self.cart,
                order=self.order,
            )