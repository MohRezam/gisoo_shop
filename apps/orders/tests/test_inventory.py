from django.test import TestCase

from apps.products.tests.factories import (
    create_brand,
    create_category,
    create_product,
    create_product_variant,
)
from apps.orders.services.inventory import reserve_stock


class ReserveStockTests(TestCase):

    def setUp(self):
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

    def test_reduce_stock(self):
        reserve_stock(
            variants=[
                (
                    self.variant,
                    3,
                )
            ]
        )

        self.variant.refresh_from_db()

        self.assertEqual(
            self.variant.stock,
            7,
        )

    def test_reduce_stock_multiple_times(self):
        reserve_stock(
            variants=[
                (
                    self.variant,
                    2,
                )
            ]
        )

        reserve_stock(
            variants=[
                (
                    self.variant,
                    1,
                )
            ]
        )

        self.variant.refresh_from_db()

        self.assertEqual(
            self.variant.stock,
            7,
        )

    def test_reduce_stock_multiple_variants(self):
        product2 = create_product(
            category=self.variant.product.category,
            brand=self.variant.product.brand,
            slug="product-2",
            title="Product 2",
        )

        variant2 = create_product_variant(
            product=product2,
            sku="sku-2",
            price=50000,
        )

        reserve_stock(
            variants=[
                (
                    self.variant,
                    2,
                ),
                (
                    variant2,
                    4,
                ),
            ]
        )

        self.variant.refresh_from_db()
        variant2.refresh_from_db()

        self.assertEqual(
            self.variant.stock,
            8,
        )

        self.assertEqual(
            variant2.stock,
            6,
        )