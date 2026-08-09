from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.products.tests.factories import (
    create_brand,
    create_category,
    create_product,
    create_product_variant,
)


class ProductListAPITests(APITestCase):

    def setUp(self):
        self.url = reverse("apps.products:product-list")

        self.category = create_category(
            slug="category-1",
        )

        self.brand = create_brand(
            slug="brand-1",
        )

    def test_list_products(self):
        product = create_product(
            category=self.category,
            brand=self.brand,
            slug="product-1",
        )

        create_product_variant(
            product=product,
            price=100000,
        )

        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

        self.assertEqual(
            len(response.data["results"]),
            1,
        )

    def test_only_available_products_are_returned(self):
        available = create_product(
            category=self.category,
            brand=self.brand,
            slug="available",
        )

        unavailable = create_product(
            category=self.category,
            brand=self.brand,
            slug="unavailable",
        )

        available.is_available = True
        available.save()

        unavailable.is_available = False
        unavailable.save()

        create_product_variant(
            product=available,
        )

        create_product_variant(
            product=unavailable,
            sku="sku-2",
        )

        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

        self.assertEqual(
            len(response.data["results"]),
            1,
        )

        self.assertEqual(
            response.data["results"][0]["slug"],
            "available",
        )
