from rest_framework import serializers

from apps.home.models import FAQCategory, FAQ


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = [
            "id",
            "question",
            "answer",
        ]


class FAQCategorySerializer(serializers.ModelSerializer):
    questions = FAQSerializer(
        source="faqs",
        many=True,
        read_only=True,
    )

    class Meta:
        model = FAQCategory
        fields = [
            "id",
            "title",
            "slug",
            "questions",
        ]
