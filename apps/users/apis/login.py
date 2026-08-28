import time

from django.contrib.auth import get_user_model
from django.core.cache import cache

from rest_framework import status
from rest_framework.exceptions import Throttled
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext as _

from apps.consultations.services import (
    merge_guest_consultations_after_login,
)
from apps.products.services.wishlist import (
    WishlistService,
)
from apps.users.models import UserPhoneNumber

from apps.users.serializers.login import (
    RequestOTPSerializer,
    VerifyOTPSerializer,
)
from core_gisoo_backend.settings.components.constants import WISHLIST_COOKIE_NAME

from utils.general.throttles import (
    OTPThrottle,
)

from django.db import transaction

User = get_user_model()


class RequestOTPAPIView(APIView):
    serializer_class = RequestOTPSerializer
    throttle_classes = [OTPThrottle]

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

        otp = "123456"

        cache.set(
            f"otp_{phone_number}",
            otp,
            123,
        )

        return Response(
            {
                "detail": "OTP code sent successfully.",
            },
            status=status.HTTP_200_OK,
        )


class ResendOTPAPIView(APIView):
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

        otp_key = f"otp_{phone_number}"
        otp_timestamp_key = (
            f"otp_timestamp_{phone_number}"
        )
        otp_request_count_key = (
            f"otp_request_count_{phone_number}"
        )

        request_count = cache.get(
            otp_request_count_key,
            0,
        )

        if request_count >= 5:
            raise Throttled(
                detail=_(
                    "You have exceeded the maximum "
                    "number of OTP requests. "
                    "Please try again later."
                )
            )

        last_sent_timestamp = cache.get(
            otp_timestamp_key
        )

        if last_sent_timestamp:
            elapsed = (
                    time.time()
                    - last_sent_timestamp
            )

            if elapsed < 60:
                raise Throttled(
                    detail=_(
                        "Please wait {} seconds "
                        "before resending the OTP."
                    ).format(
                        int(60 - elapsed)
                    )
                )

        otp = "123456"

        cache.set(
            otp_key,
            otp,
            123,
        )

        cache.set(
            otp_timestamp_key,
            time.time(),
            timeout=300,
        )

        cache.set(
            otp_request_count_key,
            request_count + 1,
            timeout=300,
        )

        return Response(
            {
                "detail": "OTP code resent successfully.",
            },
            status=status.HTTP_200_OK,
        )


class VerifyOTPAPIView(APIView):
    serializer_class = VerifyOTPSerializer

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


        user_phone = (
            UserPhoneNumber.objects
            .select_related("user")
            .filter(
                phone_number=phone_number,
                is_verified=True,
            )
            .first()
        )

        if user_phone:
            user = user_phone.user
            created = False

        else:
            user, created = User.objects.get_or_create(
                phone_number=phone_number
            )

            UserPhoneNumber.objects.get_or_create(
                user=user,
                phone_number=phone_number,
                defaults={
                    "is_verified": True,
                    "is_primary": True,
                },
            )

        WishlistService.merge_wishlist_after_login(
            request=request,
            user=user,
        )

        merge_guest_consultations_after_login(
            user,
        )

        refresh = RefreshToken.for_user(user)

        access_token = str(
            refresh.access_token
        )

        cache.delete(
            f"otp_{phone_number}"
        )

        response = Response(
            {
                "access_token": access_token,
                "refresh_token": str(refresh),
                "is_new_user": created,
            },
            status=status.HTTP_200_OK,
        )

        response.delete_cookie(
            WISHLIST_COOKIE_NAME
        )

        return response
