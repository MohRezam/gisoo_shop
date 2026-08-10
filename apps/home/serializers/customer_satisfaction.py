from rest_framework import serializers

from apps.home.models import CustomerSatisfaction


class CustomerSatisfactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerSatisfaction
        fields = ["id", "image"]