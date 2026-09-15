from django.contrib import admin

from apps.notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "notification_type",
        "channel",
        "status",
        "recipient",
        "user",
        "created_at",
        "sent_at",
    )

    list_filter = (
        "notification_type",
        "channel",
        "status",
        "created_at",
    )

    search_fields = (
        "recipient",
        "provider_message_id",
        "error_message",
        "user__phone_number",
    )

    readonly_fields = (
        "user",
        "notification_type",
        "channel",
        "status",
        "recipient",
        "title",
        "message",
        "provider_message_id",
        "error_message",
        "created_at",
        "sent_at",
    )

    ordering = ("-created_at",)

    list_per_page = 50