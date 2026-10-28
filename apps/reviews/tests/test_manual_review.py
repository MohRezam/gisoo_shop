from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.products.tests.factories import create_brand, create_category, create_product
from apps.reviews.models import ProductReview, ReviewStatus
from apps.reviews.serializers import ProductReviewPublicSerializer

User = get_user_model()


class ManualReviewTests(TestCase):
    def setUp(self):
        self.product = create_product(
            category=create_category(slug="rev-cat"),
            brand=create_brand(slug="rev-brand"),
            slug="rev-product",
        )

    def test_manual_review_needs_no_user(self):
        review = ProductReview(
            product=self.product,
            author_name="سارا م.",
            rating=5,
            comment="خیلی خوب بود",
            status=ReviewStatus.APPROVED,
        )
        review.full_clean()
        review.save()

        self.assertIsNone(review.user_id)
        self.assertEqual(
            ProductReviewPublicSerializer(review).data["author_name"],
            "سارا م.",
        )

    def test_manual_review_without_name_is_rejected(self):
        review = ProductReview(
            product=self.product,
            rating=4,
            comment="بدون نام",
            status=ReviewStatus.APPROVED,
        )
        with self.assertRaises(ValidationError):
            review.full_clean()

    def test_customer_review_still_uses_account_name(self):
        user = User.objects.create_user(
            phone_number="09120000021",
            first_name="نگار",
            last_name="کریمی",
        )
        review = ProductReview.objects.create(
            user=user,
            product=self.product,
            rating=5,
            comment="از خودم",
            status=ReviewStatus.APPROVED,
        )
        self.assertEqual(
            ProductReviewPublicSerializer(review).data["author_name"],
            "نگار کریمی",
        )
