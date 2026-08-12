from rest_framework import serializers



class MarketingSubscribeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=11,
        min_length=11,
    )

    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError(
                "Phone number must contain only digits."
            )

        if not value.startswith("09"):
            raise serializers.ValidationError(
                "Enter a valid Iranian mobile number."
            )

        return value


class MarketingVerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=11,
        min_length=11,
    )

    otp = serializers.CharField(
        max_length=6,
        min_length=6,
    )

    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError(
                "Phone number must contain only digits."
            )

        if not value.startswith("09"):
            raise serializers.ValidationError(
                "Enter a valid Iranian mobile number."
            )

        return value

    def validate_otp(self, value):
        if not value.isdigit():
            raise serializers.ValidationError(
                "OTP must contain only digits."
            )

        return value