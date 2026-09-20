from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase

from apps.addresses.tests.factories import create_address
from apps.cart.tests.factories import create_cart, create_cart_item
from apps.orders.models import OrderStatus
from apps.orders.services.create_order import create_order
from apps.orders.tests.factories import create_shipping_method
from apps.payments.models import (
    PaymentDestinationCard,
    PaymentIntent,
    PaymentIntentStatus,
)
from apps.payments.services.review_payment_intent import (
    approve_payment_intent,
    reject_payment_intent,
)
from apps.products.tests.factories import (
    create_brand,
    create_category,
    create_product,
    create_product_variant,
)

User = get_user_model()


def make_test_image(name="receipt.png"):
    try:
        from PIL import Image
    except ImportError:
        # minimal valid-ish fallback; tests needing ImageField need Pillow
        content = b"\x89PNG\r\n\x1a\n"
        return SimpleUploadedFile(name, content, content_type="image/png")

    buf = BytesIO()
    Image.new("RGB", (16, 16), color=(255, 0, 0)).save(buf, format="PNG")
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/png")


class PaymentIntentAPITests(APITestCase):

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(phone_number="09120000001")
        self.client.force_authenticate(self.user)

        PaymentDestinationCard.objects.create(
            card_number="6037991122334455",
            bank_name="Bank Test",
            holder_name="Gisoo",
            is_active=True,
        )

        self.address = create_address(user=self.user, phone_number="09120000001")
        self.shipping = create_shipping_method(title="Post-PI-1")

        category = create_category(slug="cat-pi")
        brand = create_brand(slug="brand-pi")
        product = create_product(category=category, brand=brand, slug="prod-pi")
        variant = create_product_variant(product=product, sku="sku-pi", stock=10)

        cart = create_cart(user=self.user)
        create_cart_item(cart=cart, variant=variant, quantity=1)

        self.order = create_order(
            user=self.user,
            address_id=self.address.id,
            shipping_method_id=self.shipping.id,
        )

    def test_create_order_includes_payment_intent(self):
        intent = self.order.payment_intents.first()
        self.assertIsNotNone(intent)
        self.assertEqual(intent.status, PaymentIntentStatus.PENDING_PAYMENT)
        self.assertEqual(self.order.status, OrderStatus.WAITING_PAYMENT)
        self.assertTrue(intent.destination_card.card_number)

    def test_resume_active_intent(self):
        url = reverse(
            "apps.payments:create-payment-intent",
            kwargs={"order_id": self.order.id},
        )
        first = self.client.post(url)
        second = self.client.post(url)

        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(first.data["id"], second.data["id"])
        self.assertEqual(PaymentIntent.objects.filter(order=self.order).count(), 1)

    def test_recreate_after_reject(self):
        intent = self.order.payment_intents.first()
        intent.status = PaymentIntentStatus.UNDER_REVIEW
        intent.save(update_fields=["status"])
        reject_payment_intent(intent=intent, reason="bad")

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, OrderStatus.PAYMENT_REJECTED)

        url = reverse(
            "apps.payments:create-payment-intent",
            kwargs={"order_id": self.order.id},
        )
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], PaymentIntentStatus.PENDING_PAYMENT)
        self.assertNotEqual(response.data["id"], intent.id)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, OrderStatus.WAITING_PAYMENT)

    def test_get_by_token(self):
        intent = self.order.payment_intents.first()
        url = reverse(
            "apps.payments:payment-intent-by-token",
            kwargs={"token": intent.token},
        )
        # unauthenticated allowed
        self.client.force_authenticate(user=None)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["token"], intent.token)
        self.assertIn("destination_card", response.data)
        self.assertIn("payable_amount", response.data)

    def test_get_by_token_uses_cache(self):
        intent = self.order.payment_intents.first()
        url = reverse(
            "apps.payments:payment-intent-by-token",
            kwargs={"token": intent.token},
        )
        self.client.force_authenticate(user=None)
        first = self.client.get(url)
        # mutate DB; cache should still return old status briefly
        intent.status = PaymentIntentStatus.UNDER_REVIEW
        intent.save(update_fields=["status"])
        second = self.client.get(url)
        self.assertEqual(first.data["status"], second.data["status"])

    def test_upload_receipt(self):
        intent = self.order.payment_intents.first()
        url = reverse(
            "apps.payments:upload-payment-receipt",
            kwargs={"intent_id": intent.id},
        )
        image = make_test_image()
        response = self.client.post(
            url,
            {"receipt": image},
            format="multipart",
            HTTP_IDEMPOTENCY_KEY="key-1",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], PaymentIntentStatus.UNDER_REVIEW)
        self.assertFalse(response.data["can_upload_receipt"])

    def test_approve_moves_order_to_preparing(self):
        intent = self.order.payment_intents.first()
        intent.status = PaymentIntentStatus.UNDER_REVIEW
        intent.save(update_fields=["status"])
        approve_payment_intent(intent=intent)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, OrderStatus.PREPARING)
        intent.refresh_from_db()
        self.assertEqual(intent.status, PaymentIntentStatus.PAID)

    def test_response_has_required_fields(self):
        intent = self.order.payment_intents.first()
        url = reverse(
            "apps.payments:create-payment-intent",
            kwargs={"order_id": self.order.id},
        )
        response = self.client.post(url)
        for field in (
            "id",
            "token",
            "status",
            "payable_amount",
            "destination_card",
            "bank_name",
            "holder_name",
            "expires_at",
            "order_id",
            "can_upload_receipt",
            "public_number",
        ):
            self.assertIn(field, response.data)
