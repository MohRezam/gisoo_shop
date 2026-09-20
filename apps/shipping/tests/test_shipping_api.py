from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.shipping.models import ShippingMethod
from apps.shipping.cache import SHIPPING_METHODS_CACHE_KEY

User = get_user_model()


class ShippingAndAddressAPITests(APITestCase):

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(phone_number="09120000005")
        self.client.force_authenticate(self.user)
        ShippingMethod.objects.create(
            title="Post-Ship-Cache",
            price=45000,
            free_shipping_minimum=900000,
            estimated_days=2,
            is_active=True,
        )

    def test_shipping_methods_fields(self):
        url = reverse("apps.shipping:shipping-methods")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        # may be paginated or plain list
        items = data["results"] if isinstance(data, dict) and "results" in data else data
        self.assertGreaterEqual(len(items), 1)
        item = items[0]
        self.assertIn("price", item)
        self.assertIn("free_shipping_minimum", item)

    def test_shipping_methods_cached(self):
        url = reverse("apps.shipping:shipping-methods")
        self.client.get(url)
        self.assertIsNotNone(cache.get(SHIPPING_METHODS_CACHE_KEY))

        ShippingMethod.objects.create(
            title="Post-Ship-New",
            price=1000,
            free_shipping_minimum=0,
            estimated_days=1,
            is_active=True,
        )
        # signal should invalidate; next get rebuilds
        self.assertIsNone(cache.get(SHIPPING_METHODS_CACHE_KEY))
        response = self.client.get(url)
        items = (
            response.data["results"]
            if isinstance(response.data, dict) and "results" in response.data
            else response.data
        )
        titles = [i["title"] for i in items]
        self.assertIn("Post-Ship-New", titles)

    def test_create_address_returns_id(self):
        url = reverse("apps.addresses:addresses-list")
        response = self.client.post(
            url,
            {
                "title": "home",
                "receiver_name": "Ali",
                "phone_number": "09120000005",
                "province": "Tehran",
                "city": "Tehran",
                "postal_code": "1234567890",
                "address": "Street 1",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertEqual(response.data["title"], "home")
