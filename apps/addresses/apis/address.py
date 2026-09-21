from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.addresses.models import Address
from apps.addresses.serializers import (
    AddressSerializer,
    CreateAddressSerializer,
    UpdateAddressSerializer,
)
from apps.addresses.services.address import (
    create_address,
    set_default_address,
    delete_address,
)
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema_view(
    create=extend_schema(
        tags=["Addresses"],
        summary="Create address",
        description="Creates an address and returns the full object including `id`.",
        responses={201: AddressSerializer},
    ),
)
class AddressViewSet(ModelViewSet):
    permission_classes = [
        IsAuthenticated
    ]

    def get_queryset(self):
        return Address.objects.filter(
            user=self.request.user,
            archived=False,
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        address = create_address(
            user=request.user,
            **serializer.validated_data,
        )
        return Response(
            AddressSerializer(address, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    def perform_update(
            self,
            serializer,
    ):
        make_default = serializer.validated_data.pop(
            "make_default",
            False,
        )
        address = serializer.save()

        if make_default:
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
