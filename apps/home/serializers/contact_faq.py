from rest_framework import serializers

from apps.home.models import ContactFAQ


class ContactFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactFAQ
        fields = (
            "id",
            "question",
            "answer",
        )
