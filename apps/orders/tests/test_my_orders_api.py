from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.addresses.tests.factories import create_address
from apps.cart.tests.factories import create_cart, create_cart_item
from apps.orders.models import OrderStatus
from apps.orders.services.create_order import create_order
from apps.orders.tests.factories import create_shipping_method
from apps.products.tests.factories import (
    create_brand,
    create_category,
    create_product,
    create_product_variant,
)

User = get_user_model()


class MyOrdersAndTrackAPITests(APITestCase):

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
        # rebuild cart for another order
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
        self.assertIn("destination_card", response.data["payment_intent"])

    def test_my_orders_list(self):
        url = reverse("apps.orders:my-orders")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["count"], 1)
        self.assertIn("results", response.data)
        self.assertIn("public_number", response.data["results"][0])

    def test_my_latest_order(self):
        url = reverse("apps.orders:my-latest-order")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.order.id)

    def test_track_order(self):
        url = reverse("apps.orders:track-order")
        self.client.force_authenticate(user=None)
        response = self.client.get(
            url,
            {
                "code": self.order.public_number,
                "phone": self.order.phone_number,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["public_number"], self.order.public_number)
        self.assertIn("steps", response.data)
        self.assertIn("status_label", response.data)

    def test_track_order_not_found(self):
        url = reverse("apps.orders:track-order")
        response = self.client.get(
            url,
            {"code": "GS-000000-00000", "phone": "09120000002"},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_track_uses_cache(self):
        url = reverse("apps.orders:track-order")
        params = {
            "code": self.order.public_number,
            "phone": self.order.phone_number,
        }
        first = self.client.get(url, params)
        self.order.status = OrderStatus.PREPARING
        self.order.save(update_fields=["status"])
        second = self.client.get(url, params)
        # cached payload keeps previous status until TTL / invalidate
        self.assertEqual(first.data["status"], second.data["status"])
