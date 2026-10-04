from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.addresses.models import Address


phone_number_validator = RegexValidator(
    regex=r"^09\d{9}$",
    message=_("Enter a valid Iranian mobile phone number."),
)


def validate_iranian_postal_code(value):
    if value in (None, ""):
        return value
    if not str(value).isdigit() or len(str(value)) != 10:
        raise serializers.ValidationError(
            _("Enter a valid 10-digit postal code.")
        )
    return value


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address

        fields = (
            "id",
            "title",
            "receiver_name",
            "phone_number",
            "province",
            "city",
            "postal_code",
            "address",
            "is_default",
        )

        read_only_fields = (
            "id",
            "is_default",
        )


class CreateAddressSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(
        min_length=11,
        max_length=11,
        validators=[phone_number_validator],
    )
    postal_code = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=20,
    )

    class Meta:
        model = Address

        fields = (
            "title",
            "receiver_name",
            "phone_number",
            "province",
            "city",
            "postal_code",
            "address",
        )

    def validate_postal_code(self, value):
        return validate_iranian_postal_code(value)


class UpdateAddressSerializer(serializers.ModelSerializer):
    make_default = serializers.BooleanField(
        required=False,
        write_only=True,
    )
    phone_number = serializers.CharField(
        required=False,
        min_length=11,
        max_length=11,
        validators=[phone_number_validator],
    )
    postal_code = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=20,
    )

    class Meta:
        model = Address

        fields = (
            "title",
            "receiver_name",
            "phone_number",
            "province",
            "city",
            "postal_code",
            "address",
            "make_default",
        )

    def validate_postal_code(self, value):
        return validate_iranian_postal_code(value)

    def update(self, instance, validated_data):
        validated_data.pop("make_default", None)
        return super().update(instance, validated_data)
