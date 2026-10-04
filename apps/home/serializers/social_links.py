from rest_framework import serializers

from apps.home.models import SocialLinks


class SocialLinksSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLinks
        fields = (
            "telegram_url",
            "instagram_url",
            "whatsapp_url",
            "bale_url",
        )
