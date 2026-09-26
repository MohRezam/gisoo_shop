from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.products.models import DiscountCampaign
from apps.products.services.discount_campaign import end_discount_campaign
from apps.products.tests.factories import (
    create_brand,
    create_category,
    create_product,
    create_product_variant,
)


class DiscountCampaignEndTests(TestCase):
    def setUp(self):
        self.category = create_category(slug="cat-camp")
        self.brand = create_brand(slug="brand-camp")
        self.product = create_product(
            category=self.category,
            brand=self.brand,
            slug="prod-camp",
            title="Campaign Product",
        )
        self.product.show_in_special_offer = True
        self.product.save(update_fields=["show_in_special_offer"])
        self.variant = create_product_variant(
            product=self.product,
            sku="sku-camp",
            stock=5,
            price=100_000,
            discounted_price=70_000,
        )
        now = timezone.now()
        self.campaign = DiscountCampaign.objects.create(
            title="Test Campaign",
            starts_at=now - timedelta(days=2),
            ends_at=now - timedelta(minutes=1),
            is_active=True,
        )

    def test_end_campaign_clears_discount_and_flag(self):
        ended = end_discount_campaign(campaign_id=self.campaign.id)
        self.assertTrue(ended)

        self.variant.refresh_from_db()
        self.product.refresh_from_db()
        self.campaign.refresh_from_db()

        self.assertIsNone(self.variant.discounted_price)
        self.assertFalse(self.product.show_in_special_offer)
        self.assertFalse(self.campaign.is_active)

    def test_end_campaign_idempotent(self):
        self.assertTrue(end_discount_campaign(campaign_id=self.campaign.id))
        self.assertTrue(end_discount_campaign(campaign_id=self.campaign.id))
        self.variant.refresh_from_db()
        self.assertIsNone(self.variant.discounted_price)

    def test_running_campaign_not_ended_early(self):
        now = timezone.now()
        self.campaign.starts_at = now - timedelta(hours=1)
        self.campaign.ends_at = now + timedelta(hours=1)
        self.campaign.save(update_fields=["starts_at", "ends_at", "updated_at"])

        ended = end_discount_campaign(campaign_id=self.campaign.id)
        self.assertFalse(ended)

        self.variant.refresh_from_db()
        self.assertEqual(self.variant.discounted_price, 70_000)
