from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.cart.models import Cart
from apps.products.tests.factories import (
    create_brand,
    create_category,
    create_product,
    create_product_variant,
)
import uuid

class AddToCartAPITests(APITestCase):

    def setUp(self):
        self.url = reverse("apps.cart:add-to-cart")

        self.category = create_category(
            slug="category-1",
        )

        self.brand = create_brand(
            slug="brand-1",
        )

        self.product = create_product(
            category=self.category,
            brand=self.brand,
            slug="product-1",
        )

        self.variant = create_product_variant(
            product=self.product,
            sku="sku-1",
            stock=10,
            price=100000,
        )

    def test_add_item_to_cart(self):
        response = self.client.post(
            self.url,
            {
                "variant_id": self.variant.id,
                "quantity": 2,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "cart_uuid",
            response.data,
        )

        cart = Cart.objects.get(
            uuid=response.data["cart_uuid"],
        )

        self.assertEqual(
            cart.items.count(),
            1,
        )

        item = cart.items.first()

        self.assertEqual(
            item.quantity,
            2,
        )

    def test_add_existing_item_increases_quantity(self):
        response = self.client.post(
            self.url,
            {
                "variant_id": self.variant.id,
                "quantity": 2,
            },
            format="json",
        )

        cart_uuid = response.data["cart_uuid"]

        response = self.client.post(
            self.url,
            {
                "variant_id": self.variant.id,
                "quantity": 3,
            },
            format="json",
            HTTP_X_CART_UUID=cart_uuid,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        cart = Cart.objects.get(
            uuid=cart_uuid,
        )

        item = cart.items.first()

        self.assertEqual(
            item.quantity,
            5,
        )

    def test_cannot_add_more_than_stock(self):
        self.variant.stock = 2

        self.variant.save(
            update_fields=[
                "stock",
            ]
        )

        response = self.client.post(
            self.url,
            {
                "variant_id": self.variant.id,
                "quantity": 5,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_total_quantity_cannot_exceed_stock(self):
        self.variant.stock = 5

        self.variant.save(
            update_fields=[
                "stock",
            ]
        )

        response = self.client.post(
            self.url,
            {
                "variant_id": self.variant.id,
                "quantity": 3,
            },
            format="json",
        )

        cart_uuid = response.data["cart_uuid"]

        response = self.client.post(
            self.url,
            {
                "variant_id": self.variant.id,
                "quantity": 3,
            },
            format="json",
            HTTP_X_CART_UUID=cart_uuid,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_get_cart(self):
        response = self.client.post(
            self.url,
            {
                "variant_id": self.variant.id,
                "quantity": 2,
            },
            format="json",
        )

        cart_uuid = response.data["cart_uuid"]

        response = self.client.get(
            reverse(
                "apps.cart:cart-detail",
                kwargs={
                    "uuid": cart_uuid,
                },
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data["items"]),
            1,
        )

        self.assertEqual(
            response.data["items"][0]["quantity"],
            2,
        )

    def test_update_cart_item(self):
        response = self.client.post(
            self.url,
            {
                "variant_id": self.variant.id,
                "quantity": 2,
            },
            format="json",
        )

        cart = Cart.objects.get(
            uuid=response.data["cart_uuid"],
        )

        item = cart.items.first()

        response = self.client.patch(
            reverse(
                "apps.cart:cart-item-update",
                kwargs={
                    "item_id": item.id,
                },
            ),
            {
                "quantity": 5,
            },
            format="json",
            HTTP_X_CART_UUID=str(cart.uuid),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        item.refresh_from_db()

        self.assertEqual(
            item.quantity,
            5,
        )

    def test_delete_cart_item(self):
        response = self.client.post(
            self.url,
            {
                "variant_id": self.variant.id,
                "quantity": 2,
            },
            format="json",
        )

        cart = Cart.objects.get(
            uuid=response.data["cart_uuid"],
        )

        item = cart.items.first()

        response = self.client.delete(
            reverse(
                "apps.cart:cart-item-delete",
                kwargs={
                    "item_id": item.id,
                },
            ),
            HTTP_X_CART_UUID=str(cart.uuid),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            cart.items.exists(),
        )

    def test_update_quantity_more_than_stock(self):
        response = self.client.post(
            self.url,
            {
                "variant_id": self.variant.id,
                "quantity": 2,
            },
            format="json",
        )

        cart = Cart.objects.get(
            uuid=response.data["cart_uuid"],
        )

        item = cart.items.first()

        self.variant.stock = 3
        self.variant.save(
            update_fields=[
                "stock",
            ]
        )

        response = self.client.patch(
            reverse(
                "apps.cart:cart-item-update",
                kwargs={
                    "item_id": item.id,
                },
            ),
            {
                "quantity": 10,
            },
            format="json",
            HTTP_X_CART_UUID=str(cart.uuid),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        item.refresh_from_db()

        self.assertEqual(
            item.quantity,
            2,
        )

    def test_delete_non_existing_item(self):
        response = self.client.delete(
            reverse(
                "apps.cart:cart-item-delete",
                kwargs={
                    "item_id": 999999,
                },
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_update_non_existing_item(self):
        response = self.client.patch(
            reverse(
                "apps.cart:cart-item-update",
                kwargs={
                    "item_id": 999999,
                },
            ),
            {
                "quantity": 2,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_get_non_existing_cart(self):
        response = self.client.get(
            reverse(
                "apps.cart:cart-detail",
                kwargs={
                    "uuid": uuid.uuid4(),
                },
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )


class CartOwnershipAPITests(APITestCase):

    def setUp(self):
        from django.contrib.auth import get_user_model
        from apps.cart.models import CartItem

        User = get_user_model()
        self.user = User.objects.create_user(
            phone_number="09121110001",
        )
        self.category = create_category(slug="own-cat")
        self.brand = create_brand(slug="own-brand")
        self.product = create_product(
            category=self.category,
            brand=self.brand,
            slug="own-product",
        )
        self.variant = create_product_variant(
            product=self.product,
            sku="own-sku",
            stock=10,
            price=100000,
        )
        self.user_cart = Cart.objects.create(
            user=self.user,
            is_active=True,
        )
        CartItem.objects.create(
            cart=self.user_cart,
            variant=self.variant,
            quantity=1,
        )

    def test_guest_cannot_view_user_cart(self):
        response = self.client.get(
            reverse(
                "apps.cart:cart-detail",
                kwargs={"uuid": self.user_cart.uuid},
            ),
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_guest_cannot_update_user_cart_item(self):
        item = self.user_cart.items.first()
        response = self.client.patch(
            reverse(
                "apps.cart:cart-item-update",
                kwargs={"item_id": item.id},
            ),
            {"quantity": 2},
            format="json",
            HTTP_X_CART_UUID=str(self.user_cart.uuid),
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )


class CartStockAggregationAPITests(APITestCase):

    def setUp(self):
        from apps.cart.tests.factories import BundleFactory

        self.url = reverse("apps.cart:add-to-cart")
        self.category = create_category(slug="agg-cat")
        self.brand = create_brand(slug="agg-brand")
        self.product = create_product(
            category=self.category,
            brand=self.brand,
            slug="agg-product",
        )
        self.variant = create_product_variant(
            product=self.product,
            sku="agg-sku",
            stock=5,
            price=100000,
        )
        self.bundle = BundleFactory(
            variant=self.variant,
            quantity=2,
            price=150000,
        )

    def test_variant_and_bundle_share_stock_budget(self):
        response = self.client.post(
            self.url,
            {
                "variant_id": self.variant.id,
                "quantity": 3,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cart_uuid = response.data["cart_uuid"]

        response = self.client.post(
            self.url,
            {
                "bundle_id": self.bundle.id,
                "quantity": 1,
            },
            format="json",
            HTTP_X_CART_UUID=cart_uuid,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            self.url,
            {
                "bundle_id": self.bundle.id,
                "quantity": 1,
            },
            format="json",
            HTTP_X_CART_UUID=cart_uuid,
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )


class CartDiscountAPITests(APITestCase):
    def setUp(self):
        self.url = reverse("apps.cart:cart-discount")
        self.add_url = reverse("apps.cart:add-to-cart")
        self.category = create_category(slug="disc-cat")
        self.brand = create_brand(slug="disc-brand")
        self.product = create_product(
            category=self.category,
            brand=self.brand,
            slug="disc-product",
        )
        self.variant = create_product_variant(
            product=self.product,
            sku="disc-sku",
            stock=10,
            price=100_000,
        )

    def _make_cart(self):
        response = self.client.post(
            self.add_url,
            {
                "variant_id": self.variant.id,
                "quantity": 1,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data["cart_uuid"]

    def test_invalid_discount_code_message(self):
        from apps.discounts.tests.factories import DiscountFactory

        cart_uuid = self._make_cart()
        DiscountFactory(code="REALCODE")

        response = self.client.post(
            self.url,
            {"code": "WRONGCODE"},
            format="json",
            HTTP_X_CART_UUID=cart_uuid,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        detail = response.data.get("error", {}).get("detail") or response.data
        self.assertIn("کد تخفیف نامعتبر میباشد", str(detail))

    def test_apply_valid_discount(self):
        from apps.discounts.tests.factories import DiscountFactory
        from apps.cart.models import Cart

        cart_uuid = self._make_cart()
        DiscountFactory(
            code="SAVE10",
            discount_type="percentage",
            value=10,
            applies_to_discounted_products=True,
        )

        response = self.client.post(
            self.url,
            {"code": "save10"},
            format="json",
            HTTP_X_CART_UUID=cart_uuid,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["discount"], "SAVE10")
        self.assertEqual(response.data["cart_uuid"], cart_uuid)
        self.assertEqual(response.data["coupon_discount"], 10_000)
        self.assertEqual(response.data["total"], 90_000)

        cart = Cart.objects.get(uuid=cart_uuid)
        self.assertEqual(cart.discount.code, "SAVE10")
