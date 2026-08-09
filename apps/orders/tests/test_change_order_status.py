from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.addresses.tests.factories import create_address
from apps.cart.tests.factories import (
    create_cart,
    create_cart_item,
)
from apps.orders.models import (
    OrderStatus,
    OrderStatusHistory,
)
from apps.orders.services.change_order_status import (
    change_order_status,
)
from apps.orders.services.create_order import create_order
from apps.orders.tests.factories import create_shipping_method
from apps.products.tests.factories import (
    create_brand,
    create_category,
    create_product,
    create_product_variant,
)

User = get_user_model()


class ChangeOrderStatusTests(TestCase):

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
        )

        cart = create_cart(
            user=self.user,
        )

        create_cart_item(
            cart=cart,
            variant=variant,
            quantity=1,
        )

        self.order = create_order(
            user=self.user,
            address_id=self.address.id,
            shipping_method_id=self.shipping.id,
        )

    def test_change_status_success(self):
        order = change_order_status(
            order=self.order,
            new_status=OrderStatus.PREPARING,
        )

        order.refresh_from_db()

        self.assertEqual(
            order.status,
            OrderStatus.PREPARING,
        )

        self.assertIsNotNone(
            order.prepared_at,
        )

        self.assertEqual(
            OrderStatusHistory.objects.count(),
            1,
        )

    def test_same_status(self):
        history_before = OrderStatusHistory.objects.count()

        order = change_order_status(
            order=self.order,
            new_status=OrderStatus.CREATED,
        )

        order.refresh_from_db()

        self.assertEqual(
            order.status,
            OrderStatus.CREATED,
        )

        self.assertEqual(
            OrderStatusHistory.objects.count(),
            history_before,
        )

    def test_invalid_transition(self):
        with self.assertRaises(ValidationError):
            change_order_status(
                order=self.order,
                new_status=OrderStatus.DELIVERED,
            )

    def test_set_shipped_at(self):
        change_order_status(
            order=self.order,
            new_status=OrderStatus.PREPARING,
        )

        order = change_order_status(
            order=self.order,
            new_status=OrderStatus.SHIPPED,
        )

        order.refresh_from_db()

        self.assertIsNotNone(
            order.shipped_at,
        )

    def test_set_delivered_at(self):
        change_order_status(
            order=self.order,
            new_status=OrderStatus.PREPARING,
        )

        change_order_status(
            order=self.order,
            new_status=OrderStatus.SHIPPED,
        )

        order = change_order_status(
            order=self.order,
            new_status=OrderStatus.DELIVERED,
        )

        order.refresh_from_db()

        self.assertIsNotNone(
            order.delivered_at,
        )

    def test_save_reason(self):
        reason = "Prepared by admin"

        change_order_status(
            order=self.order,
            new_status=OrderStatus.PREPARING,
            reason=reason,
        )

        history = OrderStatusHistory.objects.first()

        self.assertEqual(
            history.reason,
            reason,
        )

    def test_save_changed_by(self):
        admin = User.objects.create_user(
            phone_number="09121111111",
        )

        change_order_status(
            order=self.order,
            new_status=OrderStatus.PREPARING,
            changed_by=admin,
        )

        history = OrderStatusHistory.objects.first()

        self.assertEqual(
            history.changed_by,
            admin,
        )
