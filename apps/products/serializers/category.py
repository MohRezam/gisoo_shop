from apps.products.models import Category
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category

        fields = (
            "id",
            "title",
            "slug",
            "image",
            # "parent",
        )
