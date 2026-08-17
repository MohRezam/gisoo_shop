from rest_framework import serializers


class BlacklistRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)
