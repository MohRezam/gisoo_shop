from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.home.models import CustomerSatisfaction


class CustomerSatisfactionListAPIViewTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.active_satisfaction = CustomerSatisfaction.objects.create(
            image="customer_satisfaction/active.jpg",
            is_active=True,
        )

        cls.inactive_satisfaction = CustomerSatisfaction.objects.create(
            image="customer_satisfaction/inactive.jpg",
            is_active=False,
        )

    def test_customer_satisfaction_list_returns_only_active_items(self):
        url = reverse(
            "apps.home:customer-satisfaction-list"
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = response.data["results"]

        self.assertEqual(
            len(results),
            1,
        )

        self.assertEqual(
            results[0]["id"],
            self.active_satisfaction.id,
        )

    def test_customer_satisfaction_list_does_not_return_inactive_items(self):
        url = reverse(
            "apps.home:customer-satisfaction-list"
        )

        response = self.client.get(url)

        results = response.data["results"]

        returned_ids = [
            item["id"]
            for item in results
        ]

        self.assertIn(
            self.active_satisfaction.id,
            returned_ids,
        )

        self.assertNotIn(
            self.inactive_satisfaction.id,
            returned_ids,
        )

    def test_customer_satisfaction_list_returns_image(self):
        url = reverse(
            "apps.home:customer-satisfaction-list"
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = response.data["results"]

        self.assertIn(
            "image",
            results[0],
        )

    def test_customer_satisfaction_list_returns_empty_list_when_no_active_items(
        self,
    ):
        CustomerSatisfaction.objects.filter(
            is_active=True
        ).update(
            is_active=False
        )

        url = reverse(
            "apps.home:customer-satisfaction-list"
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["results"],
            [],
        )