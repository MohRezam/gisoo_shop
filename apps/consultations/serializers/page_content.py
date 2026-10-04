from rest_framework import serializers

from apps.consultations.models import ConsultationPageBlock


class ConsultationPageBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultationPageBlock
        fields = (
            "id",
            "section",
            "title",
            "description",
            "image",
        )
