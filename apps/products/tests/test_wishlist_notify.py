from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.products.models.stock_notify import WishlistStockNotify
from apps.products.tests.factories import (
    create_brand,
    create_category,
    create_product,
    create_product_variant,
)

User = get_user_model()


class WishlistNotifyAndConsultationTests(APITestCase):

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(phone_number="09120000004")
        self.client.force_authenticate(self.user)

        self.category = create_category(slug="cat-wl")
        self.brand = create_brand(slug="brand-wl")
        self.product = create_product(
            category=self.category,
            brand=self.brand,
            slug="prod-wl",
        )
        self.variant = create_product_variant(
            product=self.product,
            sku="sku-wl",
            stock=0,
        )

    def test_notify_stock_subscribe(self):
        url = reverse("apps.products:wishlist-notify-stock")
        response = self.client.post(
            url,
            {"product_id": self.product.id},
            format="json",
        )
        self.assertIn(response.status_code, (status.HTTP_200_OK, status.HTTP_201_CREATED))
        self.assertTrue(response.data["subscribed"])
        self.assertTrue(
            WishlistStockNotify.objects.filter(
                user=self.user,
                product=self.product,
                is_notified=False,
            ).exists()
        )

    def test_notify_stock_creates_inbox_when_back(self):
        WishlistStockNotify.objects.create(
            user=self.user,
            product=self.product,
            is_notified=False,
        )
        self.variant.stock = 5
        self.variant.save()

        from apps.notifications.models import InAppNotification

        self.assertTrue(
            InAppNotification.objects.filter(
                user=self.user,
                type="stock",
            ).exists()
        )
        req = WishlistStockNotify.objects.get(user=self.user, product=self.product)
        self.assertTrue(req.is_notified)

    def test_consultation_recommendations_shape(self):
        url = reverse("apps.products:consultation-recommendations")
        response = self.client.post(
            url,
            {"hair_problem_ids": [], "hair_type_ids": [], "limit": 5},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("products", response.data)

    def test_discount_campaigns_deprecated(self):
        url = reverse("apps.products:discount-campaigns")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["deprecated"])
        self.assertIn("use", response.data)
