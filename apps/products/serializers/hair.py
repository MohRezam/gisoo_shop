from apps.products.models import HairProblem
from rest_framework import serializers


class HairProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = HairProblem
        fields = (
            "id",
            "title",
            "slug",
            "image",
            "is_active"
        )
