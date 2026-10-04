from rest_framework import serializers

from apps.consultations.models import ConsultationFAQ


class ConsultationFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultationFAQ
        fields = (
            "id",
            "question",
            "answer",
        )
