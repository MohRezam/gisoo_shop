from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.home.models import FAQ, FAQCategory


class FAQCategoryListAPIViewTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.active_category = FAQCategory.objects.create(
            title="راهنمای ثبت سفارش",
            slug="order-guide",
            is_active=True,
        )

        cls.inactive_category = FAQCategory.objects.create(
            title="دسته غیرفعال",
            slug="inactive",
            is_active=False,
        )

    def test_returns_only_active_categories(self):
        url = reverse("apps.home:faq-category-list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            len(response.data),
            1,
        )
        self.assertEqual(
            response.data[0]["id"],
            self.active_category.id,
        )


class FAQListAPIViewTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.order_category = FAQCategory.objects.create(
            title="راهنمای ثبت سفارش",
            slug="order-guide",
            is_active=True,
        )

        cls.payment_category = FAQCategory.objects.create(
            title="پرداخت",
            slug="payment",
            is_active=True,
        )

        cls.order_faq = FAQ.objects.create(
            category=cls.order_category,
            question="چگونه سفارش ثبت کنم؟",
            answer="محصول مورد نظر را انتخاب کنید.",
            is_active=True,
        )

        cls.payment_faq = FAQ.objects.create(
            category=cls.payment_category,
            question="چگونه پرداخت کنم؟",
            answer="از طریق اطلاعات پرداخت اقدام کنید.",
            is_active=True,
        )

        cls.inactive_faq = FAQ.objects.create(
            category=cls.order_category,
            question="سوال غیرفعال",
            answer="پاسخ",
            is_active=False,
        )

    def test_returns_all_active_faqs(self):
        url = reverse("apps.home:faq-list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            len(response.data),
            2,
        )

    def test_filters_faqs_by_category(self):
        url = reverse("apps.home:faq-list")

        response = self.client.get(
            url,
            {"category": "order-guide"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            len(response.data),
            1,
        )
        self.assertEqual(
            response.data[0]["id"],
            self.order_faq.id,
        )

    def test_does_not_return_inactive_faqs(self):
        url = reverse("apps.home:faq-list")

        response = self.client.get(url)

        returned_ids = [
            item["id"]
            for item in response.data
        ]

        self.assertNotIn(
            self.inactive_faq.id,
            returned_ids,
        )