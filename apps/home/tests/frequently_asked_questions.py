from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.home.models import FAQ, FAQCategory


class FAQListAPIViewTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.order_category = FAQCategory.objects.create(
            title="راهنمای ثبت سفارش",
            slug="order-guide",
            is_active=True,
            ordering=1,
        )

        cls.payment_category = FAQCategory.objects.create(
            title="پرداخت صورت حساب",
            slug="payment",
            is_active=True,
            ordering=2,
        )

        cls.inactive_category = FAQCategory.objects.create(
            title="دسته غیرفعال",
            slug="inactive",
            is_active=False,
            ordering=3,
        )

        cls.order_faq = FAQ.objects.create(
            category=cls.order_category,
            question="چگونه سفارش ثبت کنم؟",
            answer="محصول مورد نظر را انتخاب کنید.",
            is_active=True,
            ordering=1,
        )

        cls.payment_faq = FAQ.objects.create(
            category=cls.payment_category,
            question="چگونه پرداخت کنم؟",
            answer="از طریق روش پرداخت موجود اقدام کنید.",
            is_active=True,
            ordering=1,
        )

        cls.inactive_faq = FAQ.objects.create(
            category=cls.order_category,
            question="سوال غیرفعال",
            answer="این سوال نباید نمایش داده شود.",
            is_active=False,
            ordering=2,
        )

        cls.faq_in_inactive_category = FAQ.objects.create(
            category=cls.inactive_category,
            question="سوال دسته غیرفعال",
            answer="این سوال هم نباید نمایش داده شود.",
            is_active=True,
        )

    def test_returns_only_active_categories(self):
        url = reverse("apps.home:faq-list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = response.data["results"]

        self.assertEqual(
            len(results),
            2,
        )

    def test_returns_questions_inside_categories(self):
        url = reverse("apps.home:faq-list")

        response = self.client.get(url)

        results = response.data["results"]

        order_category = next(
            item
            for item in results
            if item["id"] == self.order_category.id
        )

        self.assertEqual(
            len(order_category["questions"]),
            1,
        )

        self.assertEqual(
            order_category["questions"][0]["id"],
            self.order_faq.id,
        )

    def test_does_not_return_inactive_questions(self):
        url = reverse("apps.home:faq-list")

        response = self.client.get(url)

        results = response.data["results"]

        all_questions = [
            question
            for category in results
            for question in category["questions"]
        ]

        question_ids = [
            question["id"]
            for question in all_questions
        ]

        self.assertNotIn(
            self.inactive_faq.id,
            question_ids,
        )

    def test_does_not_return_questions_from_inactive_categories(self):
        url = reverse("apps.home:faq-list")

        response = self.client.get(url)

        results = response.data["results"]

        category_ids = [
            category["id"]
            for category in results
        ]

        self.assertNotIn(
            self.inactive_category.id,
            category_ids,
        )

    def test_returns_empty_questions_for_category_without_active_faqs(self):
        category = FAQCategory.objects.create(
            title="بدون سوال",
            slug="empty",
            is_active=True,
        )

        url = reverse("apps.home:faq-list")

        response = self.client.get(url)

        results = response.data["results"]

        category_data = next(
            item
            for item in results
            if item["id"] == category.id
        )

        self.assertEqual(
            category_data["questions"],
            [],
        )