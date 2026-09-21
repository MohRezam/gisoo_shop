from rest_framework import serializers

from apps.payments.models import PaymentGuideVideo


class PaymentGuideVideoSerializer(serializers.ModelSerializer):
    video_url = serializers.SerializerMethodField()
    poster = serializers.SerializerMethodField()

    class Meta:
        model = PaymentGuideVideo
        fields = (
            "title",
            "video_url",
            "poster",
            "is_active",
        )

    def get_video_url(self, obj: PaymentGuideVideo) -> str:
        return obj.resolved_video_url

    def get_poster(self, obj: PaymentGuideVideo) -> str | None:
        if not obj.poster:
            return None
        try:
            return obj.poster.url
        except ValueError:
            return None
