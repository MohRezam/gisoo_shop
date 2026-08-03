from rest_framework import serializers

from apps.addresses.models import Address


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


class UpdateAddressSerializer(serializers.ModelSerializer):
    make_default = serializers.BooleanField(
        required=False,
        write_only=True,
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
