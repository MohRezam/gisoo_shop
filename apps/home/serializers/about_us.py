from rest_framework import serializers

from apps.home.models import HomeAbout


class HomeAboutSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeAbout
        fields = (
            "id",
            "title",
            "description",
            "image",
        )