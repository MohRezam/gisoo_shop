from rest_framework import serializers

from apps.users.models import UserPhoneNumber
from django.utils.translation import gettext_lazy as _


class UserPhoneNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPhoneNumber
        fields = (
            "id",
            "phone_number",
            "is_verified",
            "is_primary",
            "created_at",
        )

        read_only_fields = (
            "id",
            "is_verified",
            "created_at",
        )

    def validate_phone_number(self, value):
        user = self.context["request"].user

        queryset = UserPhoneNumber.objects.filter(
            phone_number=value
        ).exclude(
            user=user
        )

        if queryset.exists():
            raise serializers.ValidationError(
                _("This phone number is already registered.")
            )

        return value

    def validate(self, attrs):
        is_primary = attrs.get("is_primary", False)

        if is_primary:
            if self.instance:
                if not self.instance.is_verified:
                    raise serializers.ValidationError({
                        "is_primary": _(
                            "Only a verified phone number can be primary."
                        )
                    })

        return attrs

    def create(self, validated_data):
        user = self.context["request"].user

        return UserPhoneNumber.objects.create(
            user=user,
            **validated_data,
        )
