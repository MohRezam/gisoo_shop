from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.addresses.tests.factories import create_address
from apps.cart.tests.factories import (
    create_cart,
    create_cart_item,
)
from apps.orders.models import Order
from apps.orders.tests.factories import create_shipping_method
from apps.products.tests.factories import (
    create_brand,
    create_category,
    create_product,
    create_product_variant,
)
from apps.cart.models import Cart
from django.utils import timezone

from unittest.mock import patch

User = get_user_model()


class CreateOrderAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            phone_number="09120000000",
        )

        self.client.force_authenticate(
            self.user,
        )

        self.url = reverse(
            "apps.orders:create-order",
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
            stock=10,
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

    def test_create_order(self):
        response = self.client.post(
            self.url,
            {
                "address_id": self.address.id,
                "shipping_method_id": self.shipping.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            Order.objects.count(),
            1,
        )

        order = Order.objects.first()

        self.assertEqual(
            order.user,
            self.user,
        )

    def test_create_order_with_empty_cart(self):
        cart = Cart.objects.get(
            user=self.user,
            is_active=True,
        )

        cart.items.all().delete()

        response = self.client.post(
            self.url,
            {
                "address_id": self.address.id,
                "shipping_method_id": self.shipping.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_invalid_address(self):
        response = self.client.post(
            self.url,
            {
                "address_id": 999999,
                "shipping_method_id": self.shipping.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_invalid_shipping_method(self):
        response = self.client.post(
            self.url,
            {
                "address_id": self.address.id,
                "shipping_method_id": 999999,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_payment_created(self):
        self.client.post(
            self.url,
            {
                "address_id": self.address.id,
                "shipping_method_id": self.shipping.id,
            },
            format="json",
        )

        order = Order.objects.first()

        self.assertIsNotNone(
            order.payment,
        )

        self.assertEqual(
            order.payment.amount,
            order.total_price,
        )

    def test_cart_is_cleared(self):
        self.client.post(
            self.url,
            {
                "address_id": self.address.id,
                "shipping_method_id": self.shipping.id,
            },
            format="json",
        )

        cart = Cart.objects.get(
            user=self.user,
        )

        self.assertEqual(
            cart.items.count(),
            0,
        )

    def test_stock_is_reduced(self):
        stock_before = self.variant.stock

        self.client.post(
            self.url,
            {
                "address_id": self.address.id,
                "shipping_method_id": self.shipping.id,
            },
            format="json",
        )

        self.variant.refresh_from_db()

        self.assertEqual(
            self.variant.stock,
            stock_before - 2,
        )

    def test_order_items_created(self):
        self.client.post(
            self.url,
            {
                "address_id": self.address.id,
                "shipping_method_id": self.shipping.id,
            },
            format="json",
        )

        order = Order.objects.first()

        self.assertEqual(
            order.items.count(),
            1,
        )

        item = order.items.first()

        self.assertEqual(
            item.quantity,
            2,
        )

        self.assertEqual(
            item.variant,
            self.variant,
        )

    def test_not_enough_stock(self):
        self.variant.stock = 1

        self.variant.save(
            update_fields=[
                "stock",
            ]
        )

        response = self.client.post(
            self.url,
            {
                "address_id": self.address.id,
                "shipping_method_id": self.shipping.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            Order.objects.count(),
            0,
        )

    def test_order_has_expiration(self):
        self.client.post(
            self.url,
            {
                "address_id": self.address.id,
                "shipping_method_id": self.shipping.id,
            },
            format="json",
        )

        order = Order.objects.first()

        self.assertGreater(
            order.expires_at,
            timezone.now(),
        )

    def test_order_detail(self):
        self.client.post(
            self.url,
            {
                "address_id": self.address.id,
                "shipping_method_id": self.shipping.id,
            },
            format="json",
        )

        order = Order.objects.first()

        response = self.client.get(
            reverse(
                "apps.orders:order-detail",
                kwargs={
                    "id": order.id,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            order.id,
        )

        self.assertEqual(
            response.data["status"],
            order.status,
        )

        self.assertEqual(
            response.data["total_price"],
            order.total_price,
        )

    def test_user_cannot_access_other_user_order(self):
        self.client.post(
            self.url,
            {
                "address_id": self.address.id,
                "shipping_method_id": self.shipping.id,
            },
            format="json",
        )

        order = Order.objects.first()

        other_user = User.objects.create_user(
            phone_number="09123333333",
        )

        self.client.force_authenticate(
            other_user,
        )

        response = self.client.get(
            reverse(
                "apps.orders:order-detail",
                kwargs={
                    "id": order.id,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    @patch(
        "apps.orders.services.create_order.schedule_order_expiration"
    )
    def test_schedule_expiration_called(
            self,
            mock_schedule,
    ):
        self.client.post(
            self.url,
            {
                "address_id": self.address.id,
                "shipping_method_id": self.shipping.id,
            },
            format="json",
        )

        mock_schedule.assert_called_once()


class OrderPermissionTests(APITestCase):

    def test_authentication_required(self):
        url = reverse(
            "apps.orders:create-order",
        )

        response = self.client.post(
            url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
