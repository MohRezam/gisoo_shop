from rest_framework import serializers

from apps.notifications.models import InAppNotification


class InAppNotificationSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(read_only=True, allow_null=True)

    class Meta:
        model = InAppNotification
        fields = [
            "id",
            "title",
            "body",
            "type",
            "link",
            "order_id",
            "expires_at",
            "is_read",
            "created_at",
        ]
        read_only_fields = fields
