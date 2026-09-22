from io import BytesIO

from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.home.models import Banner
from apps.products.tests.factories import (
    create_brand,
    create_category,
    create_product,
    create_product_variant,
)
from apps.shared.cache.list_cache import get_cache_version
from apps.shared.cache import namespaces as ns


def _png():
    from PIL import Image

    buf = BytesIO()
    Image.new("RGB", (8, 8), color=(0, 128, 255)).save(buf, format="PNG")
    return SimpleUploadedFile("b.png", buf.getvalue(), content_type="image/png")


class CatalogHomeCacheTests(APITestCase):

    def setUp(self):
        cache.clear()
        self.category = create_category(slug="cache-cat")
        self.brand = create_brand(slug="cache-brand")
        self.product = create_product(
            category=self.category,
            brand=self.brand,
            slug="cache-product",
            title="Cached Product",
        )
        create_product_variant(product=self.product, sku="cache-sku")

    def test_product_list_is_cached(self):
        url = reverse("apps.products:product-list")
        first = self.client.get(url)
        self.assertEqual(first.status_code, status.HTTP_200_OK)
        version = get_cache_version(ns.PRODUCTS_LIST)
        self.assertGreaterEqual(version, 1)

        # Same query should be served from cache (stale title until bump).
        self.product.title = "Updated Title"
        Product = self.product.__class__
        Product.objects.filter(pk=self.product.pk).update(title="Updated Title")

        second = self.client.get(url)
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        titles = [p["title"] for p in second.data.get("results", second.data)]
        self.assertIn("Cached Product", titles)

        # Signal bump on save refreshes list cache.
        self.product.title = "Updated Title"
        self.product.save()
        third = self.client.get(url)
        titles3 = [p["title"] for p in third.data.get("results", third.data)]
        self.assertIn("Updated Title", titles3)

    def test_banner_list_is_cached_and_invalidated(self):
        Banner.objects.create(
            title="Banner A",
            image=_png(),
            link_type=Banner.LinkType.NONE,
            is_active=True,
            display_order=1,
        )
        url = reverse("apps.home:banner")
        first = self.client.get(url)
        self.assertEqual(first.status_code, status.HTTP_200_OK)

        Banner.objects.create(
            title="Banner B",
            image=_png(),
            link_type=Banner.LinkType.NONE,
            is_active=True,
            display_order=2,
        )
        second = self.client.get(url)
        payload = second.data.get("results", second.data)
        titles = [b.get("title") for b in payload]
        self.assertIn("Banner B", titles)
