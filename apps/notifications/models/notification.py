from django.conf import settings
from django.db import models

from apps.notifications.constants import (
    NotificationChannel,
    NotificationStatus,
    NotificationType,
)


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="notifications",
        null=True,
        blank=True,
    )

    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
    )

    channel = models.CharField(
        max_length=20,
        choices=NotificationChannel.choices,
    )

    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
    )

    recipient = models.CharField(
        max_length=255,
    )

    title = models.CharField(
        max_length=255,
        blank=True,
    )

    message = models.TextField(
        blank=True,
    )

    provider_message_id = models.CharField(
        max_length=255,
        blank=True,
    )

    error_message = models.TextField(
        blank=True,
    )

    idempotency_key = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    sent_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]
        indexes = [
            models.Index(
                fields=[
                    "user",
                    "notification_type",
                ]
            ),
            models.Index(
                fields=[
                    "status",
                ]
            ),
            models.Index(
                fields=[
                    "channel",
                ]
            ),
        ]

    def __str__(self):
        return (
            f"{self.notification_type} "
            f"-> {self.recipient} "
            f"({self.status})"
        )