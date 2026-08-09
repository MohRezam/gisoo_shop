from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.addresses.tests.factories import create_address
from apps.cart.tests.factories import (
    create_cart,
    create_cart_item,
)
from apps.orders.models import (
    OrderStatus,
)
from apps.orders.services.create_order import create_order
from apps.orders.tasks import expire_order
from apps.orders.tests.factories import create_shipping_method
from apps.payments.models import PaymentStatus
from apps.products.tests.factories import (
    create_brand,
    create_category,
    create_product,
    create_product_variant,
)

User = get_user_model()


class ExpireOrderTests(TestCase):

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

        self.variant = create_product_variant(
            product=product,
            sku="sku-1",
            price=100000,
        )

        cart = create_cart(
            user=self.user,
        )

        create_cart_item(
            cart=cart,
            variant=self.variant,
            quantity=2,
        )

        self.order = create_order(
            user=self.user,
            address_id=self.address.id,
            shipping_method_id=self.shipping.id,
        )

    @patch("apps.orders.tasks.change_order_status")
    def test_expire_order_success(
            self,
            mock_change_status,
    ):
        self.order.expires_at = (
                timezone.now() - timedelta(minutes=1)
        )

        self.order.save()

        self.variant.refresh_from_db()

        stock_before = self.variant.stock

        expire_order(
            self.order.id,
        )

        self.variant.refresh_from_db()

        self.assertEqual(
            self.variant.stock,
            stock_before + 2,
        )
        self.assertEqual(
            self.variant.stock,
            10,
        )

        mock_change_status.assert_called_once_with(
            order=self.order,
            new_status=OrderStatus.EXPIRED,
            reason="Order expired automatically.",
        )

    def test_order_not_found(self):
        expire_order(99999)

    @patch("apps.orders.tasks.change_order_status")
    def test_ignore_non_created_order(
            self,
            mock_change_status,
    ):
        self.order.status = OrderStatus.CANCELED
        self.order.save()

        expire_order(
            self.order.id,
        )

        mock_change_status.assert_not_called()

    @patch("apps.orders.tasks.change_order_status")
    def test_ignore_not_expired(
            self,
            mock_change_status,
    ):
        self.order.expires_at = (
                timezone.now() + timedelta(minutes=5)
        )

        self.order.save()

        expire_order(
            self.order.id,
        )

        mock_change_status.assert_not_called()

    @patch("apps.orders.tasks.change_order_status")
    def test_ignore_paid_order(
            self,
            mock_change_status,
    ):
        payment = self.order.payment

        payment.status = PaymentStatus.SUCCESS

        payment.save()

        self.order.expires_at = (
                timezone.now() - timedelta(minutes=1)
        )

        self.order.save()

        expire_order(
            self.order.id,
        )

        mock_change_status.assert_not_called()
