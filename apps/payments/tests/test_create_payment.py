from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.addresses.tests.factories import create_address
from apps.cart.tests.factories import (
    create_cart,
    create_cart_item,
)
from apps.orders.services.create_order import create_order
from apps.orders.tests.factories import create_shipping_method
from apps.payments.models import (
    Payment,
    PaymentStatus,
)
from apps.payments.services.create_payment import (
    create_payment,
)
from apps.products.tests.factories import (
    create_brand,
    create_category,
    create_product,
    create_product_variant,
)

User = get_user_model()


class CreatePaymentTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            phone_number="09120000000",
        )

        self.address = create_address(
            user=self.user,
        )

        self.shipping = create_shipping_method()

        category = create_category(
            slug="category-1",
        )

        brand = create_brand(
            slug="brand-1",
        )

        product = create_product(
            category=category,
            brand=brand,
            slug="product-1",
        )

        variant = create_product_variant(
            product=product,
            sku="sku-1",
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

        self.order = create_order(
            user=self.user,
            address_id=self.address.id,
            shipping_method_id=self.shipping.id,
        )

        self.order.payment.delete()

    def test_create_payment(self):
        payment = create_payment(
            order=self.order,
        )

        self.assertIsInstance(
            payment,
            Payment,
        )

        self.assertEqual(
            Payment.objects.count(),
            1,
        )

    def test_payment_amount(self):
        payment = create_payment(
            order=self.order,
        )

        self.assertEqual(
            payment.amount,
            self.order.total_price,
        )

    def test_payment_status(self):
        payment = create_payment(
            order=self.order,
        )

        self.assertEqual(
            payment.status,
            PaymentStatus.PENDING,
        )

    def test_payment_order(self):
        payment = create_payment(
            order=self.order,
        )

        self.assertEqual(
            payment.order,
            self.order,
        )
