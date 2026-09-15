from django.core.cache import cache
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


phone_number_validator = RegexValidator(
    regex=r"^09\d{9}$",
    message=_("Enter a valid Iranian mobile phone number."),
)


class RequestOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        min_length=11,
        max_length=11,
        validators=[phone_number_validator],
    )

    def validate_phone_number(self, value):
        return value


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        min_length=11,
        max_length=11,
        validators=[phone_number_validator],
    )
    otp = serializers.CharField(
        min_length=6,
        max_length=6,
    )

    def validate_otp(self, value):
        if not value.isdigit():
            raise ValidationError(_("OTP must contain only digits."))

        return value

    def validate(self, data):
        phone_number = data["phone_number"]
        otp = data["otp"]

        otp_key = f"otp_{phone_number}"
        attempts_key = f"otp_attempts_{phone_number}"

        cached_otp = cache.get(otp_key)

        if cached_otp is None:
            raise ValidationError(
                {
                    "phone_number": _(
                        "No OTP has been requested for this phone number."
                    )
                }
            )

        attempts = cache.get(attempts_key, 0)

        if attempts >= 5:
            cache.delete(otp_key)
            cache.delete(attempts_key)

            raise ValidationError(
                {
                    "otp": _(
                        "Too many incorrect attempts. "
                        "Please request a new OTP."
                    )
                }
            )

        if str(cached_otp) != otp:
            attempts += 1

            cache.set(
                attempts_key,
                attempts,
                timeout=123,
            )

            if attempts >= 5:
                cache.delete(otp_key)

            raise ValidationError(
                {
                    "otp": _("Invalid OTP.")
                }
            )

        return data