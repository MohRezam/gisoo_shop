from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.notifications.models import InAppNotification, NotificationType
from apps.notifications.services.inbox import notify_user

User = get_user_model()


class InboxAPITests(APITestCase):

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(phone_number="09120000003")
        self.client.force_authenticate(self.user)

    def test_list_empty(self):
        url = reverse("apps.notifications:inbox-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_notify_and_list(self):
        notify_user(
            user=self.user,
            title="Hello",
            body="World",
            type=NotificationType.ORDER,
            link="/account/orders/1",
            order_id=None,
        )
        url = reverse("apps.notifications:inbox-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        item = response.data["results"][0]
        self.assertEqual(item["title"], "Hello")
        self.assertFalse(item["is_read"])

    def test_unread_count_and_cache_invalidation(self):
        notify_user(user=self.user, title="A", body="B", type="system")
        notify_user(user=self.user, title="C", body="D", type="offer")

        url = reverse("apps.notifications:inbox-unread-count")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

        # second hit should still be 2 (from cache or DB)
        response2 = self.client.get(url)
        self.assertEqual(response2.data["count"], 2)

        notif = InAppNotification.objects.filter(user=self.user).first()
        read_url = reverse(
            "apps.notifications:inbox-mark-read",
            kwargs={"pk": notif.id},
        )
        self.client.post(read_url)
        response3 = self.client.get(url)
        self.assertEqual(response3.data["count"], 1)

    def test_read_all(self):
        notify_user(user=self.user, title="A", body="B")
        notify_user(user=self.user, title="C", body="D")
        url = reverse("apps.notifications:inbox-read-all")
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["updated"], 2)
        self.assertEqual(
            InAppNotification.objects.filter(user=self.user, is_read=False).count(),
            0,
        )

    def test_otp_endpoints_unchanged(self):
        # ensure OTP routes still resolve
        self.assertTrue(reverse("apps.notifications:send-otp"))
        self.assertTrue(reverse("apps.notifications:verify-otp"))
