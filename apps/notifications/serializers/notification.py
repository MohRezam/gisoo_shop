from rest_framework import serializers


class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.RegexField(
        regex=r"^09\d{9}$",
        max_length=11,
    )


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.RegexField(
        regex=r"^09\d{9}$",
    )

    otp = serializers.CharField(
        min_length=6,
        max_length=6,
    )
