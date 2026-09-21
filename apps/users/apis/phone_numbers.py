from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import UserPhoneNumber
from apps.users.serializers import (
    UserPhoneNumberSerializer,
    RequestOTPSerializer,
)
from apps.users.serializers.login import PhoneVerifyOTPSerializer
from rest_framework import status
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from django.db import transaction
from utils.general.throttles import OTPThrottle


PHONE_ALREADY_REGISTERED = _(
    "This phone number is already registered."
)


class PhoneNumberListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserPhoneNumberSerializer

    def get_queryset(self):
        return UserPhoneNumber.objects.filter(
            user=self.request.user
        )


class PhoneNumberDetailAPIView(
    generics.RetrieveDestroyAPIView
):
    permission_classes = [IsAuthenticated]
    serializer_class = UserPhoneNumberSerializer

    def get_queryset(self):
        return UserPhoneNumber.objects.filter(
            user=self.request.user
        )

    def destroy(self, request, *args, **kwargs):
        phone = self.get_object()

        if phone.is_primary:
            return Response(
                {
                    "detail": _(
                        "Primary phone number cannot be "
                        "deleted. Set another phone number "
                        "as primary first."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        phone.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class SetPrimaryPhoneNumberAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        phone = (
            UserPhoneNumber.objects
            .select_for_update()
            .filter(
                pk=pk,
                user=request.user,
            )
            .first()
        )

        if phone is None:
            return Response(
                {
                    "detail": _(
                        "Phone number not found."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not phone.is_verified:
            return Response(
                {
                    "detail": _(
                        "Only a verified phone number "
                        "can be set as primary."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        UserPhoneNumber.objects.filter(
            user=request.user,
            is_primary=True,
        ).exclude(
            pk=phone.pk
        ).update(
            is_primary=False
        )

        phone.is_primary = True
        phone.save(
            update_fields=[
                "is_primary",
                "updated_at",
            ]
        )

        user = request.user
        if user.phone_number != phone.phone_number:
            user.phone_number = phone.phone_number
            user.save(update_fields=["phone_number"])

        serializer = UserPhoneNumberSerializer(
            phone,
            context={"request": request},
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class AddPhoneNumberRequestOTPAPIView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [OTPThrottle]
    serializer_class = RequestOTPSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        phone_number = serializer.validated_data[
            "phone_number"
        ]

        user = request.user

        if (
                UserPhoneNumber.objects.filter(
                    user=user,
                    phone_number=phone_number,
                ).exists()
        ):
            return Response(
                {"detail": PHONE_ALREADY_REGISTERED},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
                UserPhoneNumber.objects.filter(
                    phone_number=phone_number,
                    is_verified=True,
                ).exists()
        ):
            return Response(
                {"detail": PHONE_ALREADY_REGISTERED},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # TODO: enable real OTP + SMS when SMS panel is available
        otp = "123456"

        cache.set(
            f"phone:otp_{user.id}_{phone_number}",
            otp,
            timeout=123,
        )

        return Response(
            {
                "detail": _(
                    "OTP code sent successfully."
                )
            },
            status=status.HTTP_200_OK,
        )


class AddPhoneNumberVerifyOTPAPIView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [OTPThrottle]
    serializer_class = PhoneVerifyOTPSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(
            raise_exception=True
        )

        phone_number = serializer.validated_data[
            "phone_number"
        ]

        user = request.user

        if UserPhoneNumber.objects.filter(
            phone_number=phone_number,
            is_verified=True,
        ).exists():
            return Response(
                {"detail": PHONE_ALREADY_REGISTERED},
                status=status.HTTP_400_BAD_REQUEST,
            )

        has_primary = UserPhoneNumber.objects.filter(
            user=user,
            is_primary=True,
        ).exists()

        phone = UserPhoneNumber.objects.create(
            user=user,
            phone_number=phone_number,
            is_verified=True,
            is_primary=not has_primary,
        )

        if phone.is_primary and user.phone_number != phone_number:
            user.phone_number = phone_number
            user.save(update_fields=["phone_number"])

        cache.delete(f"phone:otp_{user.id}_{phone_number}")
        cache.delete(f"phone:otp_attempts_{user.id}_{phone_number}")

        return Response(
            UserPhoneNumberSerializer(
                phone
            ).data,
            status=status.HTTP_201_CREATED,
        )
