from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.addresses.models import Address
from apps.addresses.serializers import (
    AddressSerializer,
    CreateAddressSerializer,
    UpdateAddressSerializer,
)
from apps.addresses.services.address import create_address, set_default_address, delete_address


class AddressViewSet(ModelViewSet):
    permission_classes = [
        IsAuthenticated
    ]

    def get_queryset(self):
        return Address.objects.filter(
            user=self.request.user
        ).order_by(
            "-is_default",
            "-created_at",
        )

    def get_serializer_class(self):
        if self.action == "create":
            return CreateAddressSerializer

        if self.action in [
            "partial_update",
            "update",
        ]:
            return UpdateAddressSerializer

        return AddressSerializer

    def perform_create(
            self,
            serializer,
    ):
        create_address(
            user=self.request.user,
            **serializer.validated_data,
        )

    def perform_update(
            self,
            serializer,
    ):
        address = serializer.save()

        if serializer.validated_data.get(
                "make_default"
        ):
            set_default_address(
                user=self.request.user,
                address=address,
            )

    def perform_destroy(
            self,
            instance,
    ):
        delete_address(
            address=instance
        )
