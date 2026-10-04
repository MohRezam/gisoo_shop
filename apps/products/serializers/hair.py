from apps.products.models import HairProblem, HairType
from rest_framework import serializers


class HairProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = HairProblem
        fields = (
            "id",
            "title",
            "slug",
            "image",
            "is_active",
        )


class HairTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = HairType
        fields = (
            "id",
            "title",
            "slug",
            "image",
            "is_active",
        )
