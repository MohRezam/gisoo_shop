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
    otp_key_prefix = "login"

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

    def get_otp_cache_keys(self, phone_number):
        prefix = self.otp_key_prefix
        return (
            f"{prefix}:otp_{phone_number}",
            f"{prefix}:otp_attempts_{phone_number}",
        )

    def validate(self, data):
        phone_number = data["phone_number"]
        otp = data["otp"]

        otp_key, attempts_key = self.get_otp_cache_keys(
            phone_number
        )

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


class PhoneVerifyOTPSerializer(VerifyOTPSerializer):
    otp_key_prefix = "phone"

    def get_otp_cache_keys(self, phone_number):
        prefix = self.otp_key_prefix
        request = self.context.get("request")
        user = getattr(request, "user", None) if request else None

        if user is not None and getattr(user, "is_authenticated", False):
            bound = f"{user.id}_{phone_number}"
            return (
                f"{prefix}:otp_{bound}",
                f"{prefix}:otp_attempts_{bound}",
            )

        return super().get_otp_cache_keys(phone_number)
