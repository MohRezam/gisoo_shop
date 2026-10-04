from django.test import TestCase

from apps.consultations.forms import (
    ConsultationRecommendationPackItemAdminForm,
)
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


class PackItemAdminFormTests(TestCase):
    def setUp(self):
        self.user = create_user(phone_number="09121112233")
        self.hair_problem = HairProblem.objects.create(
            title="ریزش",
            slug="hair-loss-pack-form",
        )
        self.consultation = ConsultationRequest.objects.create(
            user=self.user,
            full_name="تست مشاور",
            phone_number="09121112233",
            gender=ConsultationRequest.Gender.FEMALE,
            hair_problem=self.hair_problem,
            duration=ConsultationRequest.Duration.LESS_THAN_MONTH,
            status=ConsultationRequest.Status.PENDING,
        )
        brand = create_brand(title="B", slug="b-pack-form")
        category = create_category(title="C", slug="c-pack-form")
        product = create_product(
            brand=brand,
            category=category,
            title="شامپو",
            slug="shampoo-pack-form",
        )
        self.variant = create_product_variant(
            product=product,
            sku="SKU-PACK-FORM",
            stock=10,
            price=100_000,
        )
        self.pack = ConsultationRecommendationPack.objects.create(
            consultation=self.consultation,
            title="روتین صبح",
            description="هر روز استفاده شود",
        )

    def test_pack_item_creates_recommendation_from_variant(self):
        form = ConsultationRecommendationPackItemAdminForm(
            data={
                "variant": self.variant.pk,
                "display_order": 1,
            },
            instance=ConsultationRecommendationPackItem(
                pack=self.pack,
            ),
        )
        self.assertTrue(form.is_valid(), form.errors)
        item = form.save()

        self.assertEqual(item.pack_id, self.pack.pk)
        self.assertEqual(
            item.recommendation.variant_id,
            self.variant.pk,
        )
        self.assertEqual(
            ConsultationRecommendation.objects.filter(
                consultation=self.consultation,
                variant=self.variant,
            ).count(),
            1,
        )

    def test_pack_item_reuses_existing_recommendation(self):
        existing = ConsultationRecommendation.objects.create(
            consultation=self.consultation,
            variant=self.variant,
            explanation="توضیح قبلی",
            display_order=0,
        )
        form = ConsultationRecommendationPackItemAdminForm(
            data={
                "variant": self.variant.pk,
                "display_order": 2,
            },
            instance=ConsultationRecommendationPackItem(
                pack=self.pack,
            ),
        )
        self.assertTrue(form.is_valid(), form.errors)
        item = form.save()

        self.assertEqual(item.recommendation_id, existing.pk)
        self.assertEqual(
            ConsultationRecommendation.objects.filter(
                consultation=self.consultation,
                variant=self.variant,
            ).count(),
            1,
        )
        existing.refresh_from_db()
        self.assertEqual(existing.explanation, "توضیح قبلی")
