from .notification import *
from django.contrib import admin

from apps.notifications.cache import invalidate_unread_count
from apps.notifications.models import AdminAlert, InAppNotification
from apps.shared.admin import BaseModelAdmin


@admin.register(InAppNotification)
class InAppNotificationAdmin(BaseModelAdmin):
    list_display = ["id", "user", "title", "type", "is_read", "created_at"]
    list_filter = ["type", "is_read", "created_at"]
    search_fields = ["title", "body", "user__phone_number"]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.user_id:
            invalidate_unread_count(obj.user_id)

    def delete_model(self, request, obj):
        user_id = obj.user_id
        super().delete_model(request, obj)
        if user_id:
            invalidate_unread_count(user_id)

    def delete_queryset(self, request, queryset):
        user_ids = {obj.user_id for obj in queryset if obj.user_id}
        super().delete_queryset(request, queryset)
        for user_id in user_ids:
            invalidate_unread_count(user_id)


@admin.register(AdminAlert)
class AdminAlertAdmin(BaseModelAdmin):
    list_display = ["id", "title", "type", "is_read", "created_at"]
    list_filter = ["type", "is_read", "created_at"]
    list_editable = ["is_read"]
    search_fields = ["title", "body"]
    readonly_fields = ["created_at", "updated_at"]
