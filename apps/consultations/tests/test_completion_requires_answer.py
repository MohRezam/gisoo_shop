from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.consultations.models.consultation import (
    ConsultationRecommendation,
    ConsultationRecommendationPack,
    ConsultationRecommendationPackItem,
    ConsultationRequest,
)
from apps.products.models import HairProblem
from apps.products.tests.factories import (
    create_brand,
    create_category,
    create_product,
    create_product_variant,
)
from apps.users.tests.factories import create_user


class CompletionRequiresAnswerTests(TestCase):
    def setUp(self):
        self.user = create_user(phone_number="09123334455")
        self.hair_problem = HairProblem.objects.create(
            title="خشکی",
            slug="dryness-completion-req",
        )
        self.consultation = ConsultationRequest.objects.create(
            user=self.user,
            full_name="کاربر تست",
            phone_number="09123334455",
            gender=ConsultationRequest.Gender.FEMALE,
            hair_problem=self.hair_problem,
            duration=ConsultationRequest.Duration.LESS_THAN_MONTH,
            status=ConsultationRequest.Status.PENDING,
        )
        brand = create_brand(title="Brand", slug="brand-completion-req")
        category = create_category(title="Cat", slug="cat-completion-req")
        product = create_product(
            title="Product",
            slug="product-completion-req",
            brand=brand,
            category=category,
        )
        self.variant = create_product_variant(product=product)

    def test_no_answer_blocks_completed_clean(self):
        self.consultation.status = ConsultationRequest.Status.COMPLETED
        with self.assertRaises(ValidationError) as ctx:
            self.consultation.full_clean()
        self.assertIn("status", ctx.exception.message_dict)

    def test_standalone_product_allows_completed(self):
        ConsultationRecommendation.objects.create(
            consultation=self.consultation,
            variant=self.variant,
        )
        self.assertTrue(self.consultation.has_recommendation_answer())
        self.consultation.status = ConsultationRequest.Status.COMPLETED
        self.consultation.full_clean()

    def test_pack_with_item_allows_completed(self):
        pack = ConsultationRecommendationPack.objects.create(
            consultation=self.consultation,
            title="روتین",
        )
        recommendation = ConsultationRecommendation.objects.create(
            consultation=self.consultation,
            variant=self.variant,
        )
        ConsultationRecommendationPackItem.objects.create(
            pack=pack,
            recommendation=recommendation,
        )
        self.assertTrue(self.consultation.has_recommendation_answer())

    def test_empty_pack_does_not_count(self):
        ConsultationRecommendationPack.objects.create(
            consultation=self.consultation,
            title="گروه خالی",
        )
        self.assertFalse(self.consultation.has_recommendation_answer())
