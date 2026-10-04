from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.addresses.tests.factories import create_address
from apps.cart.tests.factories import create_cart, create_cart_item
from apps.orders.models import Order, OrderStatus
from apps.orders.services.create_order import create_order
from apps.orders.tests.factories import create_shipping_method
from apps.products.tests.factories import (
    create_brand,
    create_category,
    create_product,
    create_product_variant,
)
from apps.shipping.models import ShippingMethod

User = get_user_model()


class MyOrdersListAPITests(APITestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(phone_number="09120000002")
        self.client.force_authenticate(self.user)

        self.address = create_address(user=self.user, phone_number="09120000002")
        self.shipping = create_shipping_method(title="Post-Orders-1")

        category = create_category(slug="cat-ord")
        brand = create_brand(slug="brand-ord")
        product = create_product(category=category, brand=brand, slug="prod-ord")
        variant = create_product_variant(product=product, sku="sku-ord", stock=20)

        cart = create_cart(user=self.user)
        create_cart_item(cart=cart, variant=variant, quantity=1)

        self.order = create_order(
            user=self.user,
            address_id=self.address.id,
            shipping_method_id=self.shipping.id,
        )

    def test_create_order_response_shape(self):
        cart = create_cart(user=self.user)
        variant = self.order.items.first().variant
        create_cart_item(cart=cart, variant=variant, quantity=1)

        url = reverse("apps.orders:create-order")
        response = self.client.post(
            url,
            {
                "address_id": self.address.id,
                "shipping_method_id": self.shipping.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], OrderStatus.WAITING_PAYMENT)
        self.assertTrue(response.data["public_number"])
        self.assertIn("products_price", response.data)
        self.assertIn("shipping_price", response.data)
        self.assertIn("total_price", response.data)
        self.assertIsNotNone(response.data["payment_intent"])

    def test_my_orders_list_paginated(self):
        url = reverse("apps.orders:order-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["count"], 1)
        self.assertIn("results", response.data)
        self.assertIn("current", response.data)
        self.assertIn("num_pages", response.data)
        first = response.data["results"][0]
        self.assertIn("public_number", first)
        self.assertIn("status", first)
        self.assertIn("total_price", first)

    def test_my_orders_status_filter(self):
        preparing = Order.objects.create(
            user=self.user,
            public_number="ORD-PREP",
            phone_number=self.user.phone_number,
            status=OrderStatus.PREPARING,
            province="Tehran",
            city="Tehran",
            postal_code="1234567890",
            address="Test",
            shipping_method=ShippingMethod.objects.first(),
            products_price=100000,
            shipping_price=0,
            total_price=100000,
        )

        url = reverse("apps.orders:order-list")
        response = self.client.get(url, {"status": "preparing"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [row["id"] for row in response.data["results"]]
        self.assertIn(preparing.id, ids)
        self.assertTrue(
            all(row["status"] == OrderStatus.PREPARING for row in response.data["results"])
        )

    def test_my_orders_preparing_sorted_first(self):
        shipping = ShippingMethod.objects.first()
        preparing = Order.objects.create(
            user=self.user,
            public_number="ORD-PREP-2",
            phone_number=self.user.phone_number,
            status=OrderStatus.PREPARING,
            province="Tehran",
            city="Tehran",
            postal_code="1234567890",
            address="Test",
            shipping_method=shipping,
            products_price=100000,
            shipping_price=0,
            total_price=100000,
        )
        shipped = Order.objects.create(
            user=self.user,
            public_number="ORD-SHIP",
            phone_number=self.user.phone_number,
            status=OrderStatus.SHIPPED,
            province="Tehran",
            city="Tehran",
            postal_code="1234567890",
            address="Test",
            shipping_method=shipping,
            products_price=100000,
            shipping_price=0,
            total_price=100000,
        )

        url = reverse("apps.orders:order-list")
        response = self.client.get(url, {"page_size": 50})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [row["id"] for row in response.data["results"]]
        self.assertLess(ids.index(preparing.id), ids.index(shipped.id))
        self.assertLess(ids.index(preparing.id), ids.index(self.order.id))

    def test_my_latest_order(self):
        url = reverse("apps.orders:latest-order")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.order.id)

    def test_cancel_order_while_waiting_payment(self):
        url = reverse("apps.orders:cancel-order", kwargs={"id": self.order.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, OrderStatus.CANCELED)

    def test_cancel_blocked_when_receipt_submitted(self):
        from apps.payments.models import PaymentIntentStatus

        intent = self.order.payment_intents.first()
        self.assertIsNotNone(intent)
        intent.status = PaymentIntentStatus.RECEIPT_SUBMITTED
        intent.save(update_fields=["status"])

        url = reverse("apps.orders:cancel-order", kwargs={"id": self.order.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, OrderStatus.WAITING_PAYMENT)

    def test_confirm_delivery_in_window(self):
        from datetime import timedelta

        from django.utils import timezone

        from apps.orders.services.change_order_status import change_order_status
        from apps.payments.models import PaymentIntent, PaymentIntentStatus

        PaymentIntent.objects.filter(order=self.order).update(
            status=PaymentIntentStatus.PAID,
        )
        self.order.tracking_code = "1234567890"
        self.order.carrier = "post"
        self.order.save(update_fields=["tracking_code", "carrier"])
        change_order_status(
            order=self.order,
            new_status=OrderStatus.PREPARING,
            reason="test_paid",
        )
        self.order.refresh_from_db()
        change_order_status(
            order=self.order,
            new_status=OrderStatus.SHIPPED,
            reason="test_ship",
        )
        self.order.refresh_from_db()
        self.order.shipped_at = timezone.now() - timedelta(days=4)
        self.order.save(update_fields=["shipped_at"])

        url = reverse(
            "apps.orders:confirm-delivery",
            kwargs={"id": self.order.id},
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, OrderStatus.DELIVERED)
