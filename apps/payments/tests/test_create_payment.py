from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.addresses.tests.factories import create_address
from apps.cart.tests.factories import (
    create_cart,
    create_cart_item,
)
from apps.orders.models import OrderStatus
from apps.orders.services.create_order import create_order
from apps.orders.tests.factories import create_shipping_method
from apps.payments.models import PaymentIntent, PaymentIntentStatus
from apps.payments.services.create_payment import create_payment
from apps.payments.services.create_payment_intent import (
    create_payment_intent,
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

    def test_legacy_create_payment_disabled(self):
        with self.assertRaises(NotImplementedError):
            create_payment(order=self.order)

    def test_create_order_creates_payment_intent(self):
        intent = self.order.payment_intents.first()

        self.assertIsInstance(intent, PaymentIntent)
        self.assertEqual(
            intent.status,
            PaymentIntentStatus.PENDING_PAYMENT,
        )
        self.assertEqual(
            self.order.status,
            OrderStatus.WAITING_PAYMENT,
        )

    def test_create_payment_intent_idempotent(self):
        first = self.order.payment_intents.first()
        second = create_payment_intent(
            order_id=self.order.id,
            user=self.user,
        )

        self.assertEqual(first.id, second.id)
        self.assertEqual(
            PaymentIntent.objects.filter(order=self.order).count(),
            1,
        )
