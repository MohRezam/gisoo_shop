from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.addresses.tests.factories import create_address
from apps.cart.models import Cart, CartItem
from apps.orders.services.create_order import create_order
from apps.shipping.models import ShippingMethod
from apps.payments.models import (
    DestinationCard,
    PaymentIntent,
    PaymentIntentStatus,
    PaymentReceipt,
    ShopCheckoutSettings,
)
from apps.payments.services.checkout_settings import (
    enforce_order_amount_limits,
    get_payment_expiration_minutes,
)
from apps.payments.services.create_payment_intent import generate_unique_amount
from apps.payments.services.sheba import visible_sheba
from apps.payments.services.submit_receipt import receipt_hash_used_on_other_order
from apps.products.serializers.product import RelatedProductSerializer
from apps.products.tests.factories import (
    create_brand,
    create_category,
    create_product,
    create_product_variant,
)

User = get_user_model()


def make_shipping(title):
    return ShippingMethod.objects.create(
        title=title,
        price=50_000,
        free_shipping_minimum=0,
        estimated_days=3,
        is_active=True,
    )


def make_card(**overrides):
    data = {
        "name": "دارنده تست",
        "card_number": "6037991234567890",
        "bank_name": "ملی",
        "is_active": True,
    }
    data.update(overrides)
    return DestinationCard.objects.create(**data)


class ShebaVisibilityTests(TestCase):
    def test_hidden_when_threshold_is_zero(self):
        card = make_card(
            sheba_number="IR80056001486810001234567890",
            sheba_min_amount=0,
        )
        self.assertEqual(visible_sheba(card=card, order_total_toman=5_000_000), "")

    def test_hidden_below_threshold(self):
        card = make_card(
            sheba_number="IR80056001486810001234567890",
            sheba_min_amount=2_000_000,
        )
        self.assertEqual(visible_sheba(card=card, order_total_toman=1_999_999), "")

    def test_shown_at_threshold(self):
        card = make_card(
            sheba_number="IR80056001486810001234567890",
            sheba_min_amount=2_000_000,
        )
        self.assertEqual(
            visible_sheba(card=card, order_total_toman=2_000_000),
            "IR80 0560 0148 6810 0012 3456 7890",
        )


class OrderLimitTests(TestCase):
    def test_zero_limits_do_not_block(self):
        enforce_order_amount_limits(1000)

    def test_minimum_blocks_smaller_total(self):
        ShopCheckoutSettings.objects.create(pk=1, min_order_amount=500_000)
        with self.assertRaises(ValidationError):
            enforce_order_amount_limits(499_999)

    def test_maximum_blocks_larger_total(self):
        ShopCheckoutSettings.objects.create(pk=1, max_order_amount=1_000_000)
        with self.assertRaises(ValidationError):
            enforce_order_amount_limits(1_000_001)

    def test_default_payment_window_is_twenty_minutes(self):
        self.assertEqual(get_payment_expiration_minutes(), 20)


class CheckoutNameTests(TestCase):
    def test_order_stores_customer_name_and_profile(self):
        user = User.objects.create_user(phone_number="09121111111")
        address = create_address(user=user)
        shipping = make_shipping("پست تست")
        category = create_category(slug="cat-name")
        brand = create_brand(slug="brand-name")
        product = create_product(category=category, brand=brand, slug="prod-name")
        variant = create_product_variant(product, "sku-name", 5, 200_000)
        cart = Cart.objects.create(user=user, is_active=True)
        CartItem.objects.create(cart=cart, variant=variant, quantity=1)
        make_card()

        order = create_order(
            user=user,
            address_id=address.id,
            shipping_method_id=shipping.id,
            first_name="سارا",
            last_name="محمدی",
        )

        order.refresh_from_db()
        user.refresh_from_db()
        self.assertEqual(order.customer_first_name, "سارا")
        self.assertEqual(order.customer_last_name, "محمدی")
        self.assertEqual(user.first_name, "سارا")
        self.assertEqual(user.last_name, "محمدی")
        self.assertGreater(
            order.expires_at,
            timezone.now() + timedelta(minutes=19),
        )


class UniqueAmountTests(TestCase):
    def test_expired_pending_amount_is_reusable(self):
        user = User.objects.create_user(phone_number="09122222222")
        shipping = make_shipping("پست مبلغ")
        card = make_card(card_number="6037991234567891")
        order = user.orders.create(
            phone_number=user.phone_number,
            province="تهران",
            city="تهران",
            postal_code="1234567890",
            address="خیابان تست",
            shipping_method=shipping,
            products_price=100_000,
            total_price=100_000,
        )
        base_amount = 1_000_000
        # First candidate when shuffle is a no-op (suffix 100).
        expired_amount = base_amount - ((base_amount - 100) % 1000)
        PaymentIntent.objects.create(
            order=order,
            base_amount_rial=base_amount,
            unique_suffix=100,
            adjustment_discount=base_amount - expired_amount,
            payable_amount_rial=expired_amount,
            destination_card=card,
            status=PaymentIntentStatus.PENDING_PAYMENT,
            expires_at=timezone.now() - timedelta(minutes=1),
        )

        def keep_order(self, seq):
            return None

        with patch(
            "apps.payments.services.create_payment_intent.secrets.SystemRandom.shuffle",
            keep_order,
        ):
            generated = generate_unique_amount(
                base_amount_rial=base_amount,
                destination_card=card,
            )
        self.assertEqual(generated["payable_amount_rial"], expired_amount)


class DuplicateReceiptTests(TestCase):
    def test_same_file_on_another_order_is_rejected(self):
        user = User.objects.create_user(phone_number="09123333333")
        shipping = make_shipping("پست رسید")
        card = make_card(card_number="6037991234567892")

        def make_order():
            return user.orders.create(
                phone_number=user.phone_number,
                province="تهران",
                city="تهران",
                postal_code="1234567890",
                address="خیابان تست",
                shipping_method=shipping,
                total_price=50_000,
            )

        first = PaymentIntent.objects.create(
            order=make_order(),
            base_amount_rial=500_000,
            unique_suffix=222,
            adjustment_discount=0,
            payable_amount_rial=500_222,
            destination_card=card,
            expires_at=timezone.now() + timedelta(minutes=20),
        )
        second = PaymentIntent.objects.create(
            order=make_order(),
            base_amount_rial=500_000,
            unique_suffix=223,
            adjustment_discount=0,
            payable_amount_rial=500_223,
            destination_card=card,
            expires_at=timezone.now() + timedelta(minutes=20),
        )
        PaymentReceipt.objects.create(
            payment_intent=first,
            file=ContentFile(b"receipt", name="receipt.jpg"),
            original_name="receipt.jpg",
            mime_type="image/jpeg",
            file_size=7,
            sha256="abc123",
            idempotency_key="first",
        )
        self.assertTrue(
            receipt_hash_used_on_other_order(
                sha256="abc123",
                payment_intent=second,
            )
        )
        self.assertFalse(
            receipt_hash_used_on_other_order(
                sha256="abc123",
                payment_intent=first,
            )
        )


class RelatedProductStockTests(TestCase):
    def test_out_of_stock_keeps_price_and_flags_unavailable(self):
        category = create_category(slug="cat-rel")
        brand = create_brand(slug="brand-rel")
        product = create_product(category=category, brand=brand, slug="prod-rel")
        create_product_variant(product, "sku-rel", 0, 180_000)
        data = RelatedProductSerializer(product).data
        self.assertFalse(data["is_in_stock"])
        self.assertEqual(data["price"], 180_000)
