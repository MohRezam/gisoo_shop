from .notification import *
from django.contrib import admin

from apps.notifications.models import InAppNotification
from apps.shared.admin import BaseModelAdmin


@admin.register(InAppNotification)
class InAppNotificationAdmin(BaseModelAdmin):
    list_display = ["id", "user", "title", "type", "is_read", "created_at"]
    list_filter = ["type", "is_read", "created_at"]
    search_fields = ["title", "body", "user__phone_number"]
