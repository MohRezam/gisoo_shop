from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

User = get_user_model()


class RequestOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11)

    def validate_phone_number(self, value):
        try:
            User.objects.get(phone_number=value)
        except User.DoesNotExist:
            raise ValidationError(_("There is no user with this phone number."))
        return value


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11)
    otp = serializers.CharField(max_length=6)

    def validate_phone_number(self, value):
        if not User.objects.filter(phone_number=value).exists():
            raise ValidationError(_("There is no user with this phone number."))
        return value

    def validate(self, data):
        phone_number = data["phone_number"]
        otp = data["otp"]
        if cache.get(f"otp_{phone_number}") != int(otp):
            raise ValidationError(_("Invalid OTP."))
        return data
