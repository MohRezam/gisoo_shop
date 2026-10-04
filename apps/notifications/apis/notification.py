from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.serializers import (
    SendOTPSerializer, VerifyOTPSerializer,
)
from apps.notifications.services.otp import (
    save_otp, get_otp, delete_otp,
)
from apps.users.services.get_or_create_user import get_or_create_user
from apps.users.services.otp_sms import send_otp_sms
from rest_framework_simplejwt.tokens import RefreshToken


class SendOTPAPIView(APIView):

    def post(self, request):
        serializer = SendOTPSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        phone_number = serializer.validated_data[
            "phone_number"
        ]

        code, ok = send_otp_sms(phone_number=phone_number)
        if not ok:
            return Response(
                {
                    "detail": "Failed to send OTP. Please try again later."
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        save_otp(
            phone_number,
            code,
        )

        return Response(
            {
                "message": "OTP sent successfully"
            },
            status=status.HTTP_200_OK,
        )


class VerifyOTPAPIView(APIView):

    def post(self, request):
        serializer = VerifyOTPSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        phone_number = serializer.validated_data[
            "phone_number"
        ]

        otp = serializer.validated_data[
            "otp"
        ]

        stored_otp = get_otp(
            phone_number,
        )

        if stored_otp != otp:
            return Response(
                {
                    "detail": "Invalid OTP"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = get_or_create_user(
            phone_number,
        )

        delete_otp(
            phone_number,
        )

        refresh = RefreshToken.for_user(
            user,
        )

        return Response(
            {
                "access": str(
                    refresh.access_token
                ),
                "refresh": str(
                    refresh
                ),
            }
        )
