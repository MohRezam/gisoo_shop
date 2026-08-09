from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.addresses.services.address import create_address
from apps.orders.models import OrderStatus
from apps.orders.services.create_order import create_order
from apps.orders.tests.factories import create_shipping_method, create_cart, create_cart_item
from apps.products.tests.factories import create_product_variant, create_product, create_brand, create_category

User = get_user_model()


class CreateOrderTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            phone_number="09120000000",
        )

    def test_invalid_address(self):
        with self.assertRaises(ValidationError):
            create_order(
                user=self.user,
                address_id=999,
                shipping_method_id=1,
            )

    def test_invalid_shipping_method(self):
        address = create_address(
            user=self.user,
        )

        with self.assertRaises(ValidationError):
            create_order(
                user=self.user,
                address_id=address.id,
                shipping_method_id=999,
            )

    def test_cart_not_found(self):
        address = create_address(
            user=self.user,
        )

        shipping = create_shipping_method()

        with self.assertRaises(ValidationError):
            create_order(
                user=self.user,
                address_id=address.id,
                shipping_method_id=shipping.id,
            )

    def test_empty_cart(self):
        address = create_address(
            user=self.user,
        )

        shipping = create_shipping_method()

        create_cart(
            user=self.user,
        )

        with self.assertRaises(ValidationError):
            create_order(
                user=self.user,
                address_id=address.id,
                shipping_method_id=shipping.id,
            )

    def test_create_order_success(self):
        address = create_address(
            user=self.user,
        )

        shipping = create_shipping_method()

        category = create_category()

        brand = create_brand()

        product = create_product(
            category=category,
            brand=brand,
        )

        variant = create_product_variant(
            product=product,
            price=100000,
        )

        cart = create_cart(
            user=self.user,
        )

        create_cart_item(
            cart=cart,
            variant=variant,
            quantity=2,
        )

        order = create_order(
            user=self.user,
            address_id=address.id,
            shipping_method_id=shipping.id,
        )

        self.assertEqual(
            order.status,
            OrderStatus.CREATED,
        )

        self.assertEqual(
            order.items.count(),
            1,
        )

        self.assertIsNotNone(
            order.payment,
        )

        variant.refresh_from_db()

        self.assertEqual(
            variant.stock,
            8,
        )

        cart.refresh_from_db()

        self.assertFalse(
            cart.is_active,
        )

        self.assertEqual(
            cart.items.count(),
            0,
        )

        self.assertGreater(
            order.total_price,
            0,
        )
