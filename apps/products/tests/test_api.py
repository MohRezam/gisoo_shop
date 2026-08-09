from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.products.models import HairProblem, HairType
from apps.products.tests.factories import (
    create_brand,
    create_category,
    create_product, create_product_variant, create_product_image,
)
from django.test.utils import CaptureQueriesContext
from django.db import connection


class ProductListAPIViewTests(APITestCase):

    def setUp(self):
        self.url = reverse("apps.products:product-list")

        self.category = create_category(
            slug="category-1",
        )

        self.brand = create_brand(
            slug="brand-1",
        )

    def test_list_products(self):
        product1 = create_product(
            category=self.category,
            brand=self.brand,
            title="Product 1",
            slug="product-1",
        )

        create_product_variant(
            product=product1,
            sku="sku-1",
        )

        product2 = create_product(
            category=self.category,
            brand=self.brand,
            title="Product 2",
            slug="product-2",
        )

        create_product_variant(
            product=product2,
            sku="sku-2",
        )

        response = self.client.get(
            reverse("apps.products:product-list"),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            2,
        )

        self.assertEqual(
            len(response.data["results"]),
            2,
        )

    def test_hidden_products_are_not_returned(self):
        product1 = create_product(
            category=self.category,
            brand=self.brand,
            title="Product 1",
            slug="product-1",
        )

        create_product_variant(
            product=product1,
            sku="sku-1",
        )

        product2 = create_product(
            category=self.category,
            brand=self.brand,
            title="Product 2",
            slug="product-2",
        )

        create_product_variant(
            product=product2,
            sku="sku-2",
        )

        hidden = create_product(
            category=self.category,
            brand=self.brand,
            title="Hidden",
            slug="hidden",
        )

        create_product_variant(
            product=hidden,
            sku="sku-3",
        )

        hidden.is_available = False
        hidden.save(update_fields=["is_available"])

        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            2,
        )

        slugs = [
            item["slug"]
            for item in response.data["results"]
        ]

        self.assertIn("product-1", slugs)
        self.assertIn("product-2", slugs)
        self.assertNotIn("hidden", slugs)

    def test_product_list_query_count(self):
        for i in range(10):
            create_product(
                category=self.category,
                brand=self.brand,
                title=f"Product {i}",
                slug=f"product-{i}",
            )

        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(
                reverse("apps.products:product-list"),
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertLessEqual(
            len(queries),
            5,
        )

    def test_product_detail(self):
        product = create_product(
            category=self.category,
            brand=self.brand,
            title="Test Product",
            slug="test-product",
        )

        create_product_variant(
            product=product,
            sku="sku-1",
            price=500000,
        )

        create_product_image(
            product=product,
            is_primary=True,
        )

        response = self.client.get(
            reverse(
                "apps.products:product-detail",
                kwargs={
                    "slug": product.slug,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["slug"],
            product.slug,
        )

        self.assertEqual(
            len(response.data["variants"]),
            1,
        )

        self.assertEqual(
            len(response.data["images"]),
            1,
        )

    def test_filter_by_category(self):
        category2 = create_category(
            title="Category 2",
            slug="category-2",
        )

        create_product(
            category=self.category,
            brand=self.brand,
            title="Product 1",
            slug="product-1",
        )

        create_product(
            category=category2,
            brand=self.brand,
            title="Product 2",
            slug="product-2",
        )

        response = self.client.get(
            reverse("apps.products:product-list"),
            {
                "category": self.category.id,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["slug"],
            "product-1",
        )

    def test_filter_by_brand(self):
        brand2 = create_brand(
            title="Brand 2",
            slug="brand-2",
        )

        create_product(
            category=self.category,
            brand=self.brand,
            title="Product 1",
            slug="product-1",
        )

        create_product(
            category=self.category,
            brand=brand2,
            title="Product 2",
            slug="product-2",
        )

        response = self.client.get(
            reverse("apps.products:product-list"),
            {
                "brand": self.brand.id,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["slug"],
            "product-1",
        )

    def test_search_products(self):
        create_product(
            category=self.category,
            brand=self.brand,
            title="iPhone 16",
            slug="iphone-16",
        )

        create_product(
            category=self.category,
            brand=self.brand,
            title="Galaxy S25",
            slug="galaxy-s25",
        )

        response = self.client.get(
            reverse("apps.products:product-list"),
            {
                "search": "iphone",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["slug"],
            "iphone-16",
        )

    def test_ordering_by_price(self):
        product1 = create_product(
            category=self.category,
            brand=self.brand,
            title="A",
            slug="a",
        )

        product2 = create_product(
            category=self.category,
            brand=self.brand,
            title="B",
            slug="b",
        )

        create_product_variant(
            product=product1,
            sku="sku-a",
            price=500,
        )

        create_product_variant(
            product=product2,
            sku="sku-b",
            price=100,
        )

        response = self.client.get(
            reverse("apps.products:product-list"),
            {
                "ordering": "price",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            response.data["results"][0]["slug"],
            "b",
        )

    def test_filter_by_min_price(self):
        product1 = create_product(
            category=self.category,
            brand=self.brand,
            title="Cheap",
            slug="cheap",
        )

        product2 = create_product(
            category=self.category,
            brand=self.brand,
            title="Expensive",
            slug="expensive",
        )

        create_product_variant(
            product=product1,
            sku="cheap-sku",
            price=100,
        )

        create_product_variant(
            product=product2,
            sku="expensive-sku",
            price=500,
        )

        response = self.client.get(
            reverse("apps.products:product-list"),
            {
                "min_price": 300,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["slug"],
            "expensive",
        )

    def test_filter_by_max_price(self):
        product1 = create_product(
            category=self.category,
            brand=self.brand,
            title="Cheap",
            slug="cheap",
        )

        product2 = create_product(
            category=self.category,
            brand=self.brand,
            title="Expensive",
            slug="expensive",
        )

        create_product_variant(
            product=product1,
            sku="cheap-sku",
            price=100,
        )

        create_product_variant(
            product=product2,
            sku="expensive-sku",
            price=500,
        )

        response = self.client.get(
            reverse("apps.products:product-list"),
            {
                "max_price": 200,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["slug"],
            "cheap",
        )

    def test_filter_by_category_and_price(self):
        category2 = create_category(
            title="Category 2",
            slug="category-2",
        )

        product1 = create_product(
            category=self.category,
            brand=self.brand,
            title="A",
            slug="a",
        )

        product2 = create_product(
            category=category2,
            brand=self.brand,
            title="B",
            slug="b",
        )

        create_product_variant(
            product=product1,
            sku="sku-a",
            price=200,
        )

        create_product_variant(
            product=product2,
            sku="sku-b",
            price=600,
        )

        response = self.client.get(
            reverse("apps.products:product-list"),
            {
                "category": self.category.id,
                "min_price": 100,
                "max_price": 300,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["slug"],
            "a",
        )

    def test_product_detail_not_found(self):
        response = self.client.get(
            reverse(
                "apps.products:product-detail",
                kwargs={
                    "slug": "does-not-exist",
                },
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_ordering_by_price_desc(self):
        product_a = create_product(
            category=self.category,
            brand=self.brand,
            title="A",
            slug="a",
        )

        create_product_variant(
            product=product_a,
            sku="sku-a",
            price=500000,
        )

        product_b = create_product(
            category=self.category,
            brand=self.brand,
            title="B",
            slug="b",
        )

        create_product_variant(
            product=product_b,
            sku="sku-b",
            price=100000,
        )

        response = self.client.get(
            self.url,
            {
                "ordering": "-price",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            2,
        )

        self.assertEqual(
            response.data["results"][0]["slug"],
            "a",
        )

        self.assertEqual(
            response.data["results"][1]["slug"],
            "b",
        )

    def test_filter_by_hair_problem(self):
        hair_problem_1 = HairProblem.objects.create(
            title="ریزش و کم‌پشتی",
            slug="hair-loss",
        )

        hair_problem_2 = HairProblem.objects.create(
            title="شوره و خارش",
            slug="dandruff",
        )

        product1 = create_product(
            category=self.category,
            brand=self.brand,
            title="Product 1",
            slug="product-1",
        )

        product2 = create_product(
            category=self.category,
            brand=self.brand,
            title="Product 2",
            slug="product-2",
        )

        product1.hair_problems.add(hair_problem_1)
        product2.hair_problems.add(hair_problem_2)

        response = self.client.get(
            self.url,
            {
                "hair_problem": hair_problem_1.id,
            },
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
            response.data["results"][0]["slug"],
            "product-1",
        )

    def test_filter_by_hair_type(self):
        hair_type_1 = HairType.objects.create(
            title="خشک",
            slug="dry",
        )

        hair_type_2 = HairType.objects.create(
            title="چرب",
            slug="oily",
        )

        product1 = create_product(
            category=self.category,
            brand=self.brand,
            title="Product 1",
            slug="product-1",
        )

        product2 = create_product(
            category=self.category,
            brand=self.brand,
            title="Product 2",
            slug="product-2",
        )

        product1.hair_types.add(hair_type_1)
        product2.hair_types.add(hair_type_2)

        response = self.client.get(
            self.url,
            {
                "hair_type": hair_type_1.id,
            },
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
            response.data["results"][0]["slug"],
            "product-1",
        )