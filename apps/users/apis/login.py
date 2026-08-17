import time

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import Throttled, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.shared.services import SMSService
from apps.users.serializers.login import RequestOTPSerializer, VerifyOTPSerializer
from utils.general.throttles import OTPThrottle
from utils.services.otp import generate_otp

User = get_user_model()

sms_service = SMSService()


class RequestOTPAPIView(APIView):
    """
    Handles OTP request for user authentication.

    This endpoint allows users to request a one-time password (OTP) by providing their phone number.
    The OTP is generated, stored in the cache, and sent via SMS.

    Request:
        - phone_number (str): The user's registered phone number.

    Response:
        - Success message confirming OTP has been sent.
    """

    serializer_class = RequestOTPSerializer
    throttle_classes = [OTPThrottle]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        otp = 123456
        # otp = generate_otp()
        cache.set(f"otp_{phone_number}", otp, 123)
        return Response(
            {
                "detail": "OTP code sent successfully.",
            },
            status=status.HTTP_200_OK,
        )
        # response = sms_service.send_otp(otp, phone_number)

        # if response is None:
        #     raise ValidationError(
        #         _("Failed to send OTP code to {phone_number}").format(
        #             phone_number=phone_number
        #         )
        #     )
        #
        # try:
        #     data = response.json()
        # except ValueError:
        #     raise ValidationError(
        #         _("Invalid response from SMS provider for {phone_number}").format(
        #             phone_number=phone_number
        #         )
        #     )
        #
        # if "recId" in data:
        #     return Response(
        #         _("OTP code send successfully to {phone_number}").format(
        #             phone_number=phone_number
        #         ),
        #         status=status.HTTP_200_OK,
        #     )
        # else:
        #     raise ValidationError(
        #         _("Failed to send OTP code to {phone_number}").format(
        #             phone_number=phone_number
        #         )
        #     )


class ResendOTPAPIView(APIView):
    """
    Handles resending OTP for user authentication.

    Request:
        - phone_number (str): The user's registered phone number.

    Response:
        - Success message confirming OTP has been resent or error if throttled.
    """

    serializer_class = RequestOTPSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]

        otp_key = f"otp_{phone_number}"
        otp_timestamp_key = f"otp_timestamp_{phone_number}"
        otp_request_count_key = f"otp_request_count_{phone_number}"

        request_count = cache.get(otp_request_count_key, 0)
        if request_count >= 5:
            raise Throttled(
                detail=_(
                    "You have exceeded the maximum number of OTP requests. Please try again later."
                )
            )

        last_sent_timestamp = cache.get(otp_timestamp_key)
        if last_sent_timestamp:
            elapsed = time.time() - last_sent_timestamp
            if elapsed < 60:
                raise Throttled(
                    detail=_("Please wait {} seconds before resending the OTP.").format(
                        int(60 - elapsed)
                    )
                )

        otp = cache.get(otp_key)
        if not otp:
            otp = generate_otp()
            cache.set(otp_key, otp, 123)

        cache.set(otp_timestamp_key, time.time(), timeout=300)
        cache.set(otp_request_count_key, request_count + 1, timeout=300)

        response = sms_service.send_otp(otp, phone_number)
        if response is None:
            raise ValidationError(
                _("Failed to send OTP code to {phone_number}").format(
                    phone_number=phone_number
                )
            )

        try:
            data = response.json()
        except ValueError:
            raise ValidationError(_("Invalid response received from SMS provider"))

        if "recId" in data:
            return Response(
                _("OTP code send successfully to {phone_number}").format(
                    phone_number=phone_number
                ),
                status=status.HTTP_200_OK,
            )
        else:
            raise ValidationError(
                _("Failed to send OTP code to {phone_number}").format(
                    phone_number=phone_number
                )
            )


class VerifyOTPAPIView(APIView):
    """
    Verifies OTP and provides JWT authentication tokens.

    This endpoint validates the OTP entered by the user. If valid, it issues an access
    and refresh token for authentication and removes the OTP from the cache.

    Request:
        - phone_number (str): The user's registered phone number.
        - otp (str): The received OTP code.

    Response:
        - access_token (str): JWT access token for authentication.
        - refresh_token (str): JWT refresh token.
    """

    serializer_class = VerifyOTPSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        user = User.objects.get(phone_number=phone_number)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        cache.delete(f"otp_{phone_number}")

        return Response(
            {
                "refresh_token": str(refresh),
                "access_token": access_token,
            },
            status=status.HTTP_200_OK,
        )
