from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

User = get_user_model()


class RequestOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=11
    )

    def validate_phone_number(self, value):
        return value


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=11
    )

    otp = serializers.CharField(
        max_length=6
    )

    def validate(self, data):
        phone_number = data["phone_number"]
        otp = data["otp"]

        otp_key = f"otp_{phone_number}"
        cached_otp = cache.get(otp_key)

        if cached_otp is None:
            raise ValidationError(
                {
                    "phone_number": _(
                        "No OTP has been requested for this phone number."
                    )
                }
            )

        if str(cached_otp) != otp:
            raise ValidationError(
                {
                    "otp": _("Invalid OTP.")
                }
            )

        return data
