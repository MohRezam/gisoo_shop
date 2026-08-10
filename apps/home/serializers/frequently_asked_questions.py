from rest_framework import serializers

from apps.home.models import FAQCategory, FAQ


class FAQCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQCategory
        fields = [
            "id",
            "title",
            "slug",
        ]


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = [
            "id",
            "question",
            "answer",
        ]
