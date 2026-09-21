import secrets

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.exceptions import Throttled
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.cart.services.merge_cart import CartService
from apps.consultations.services import merge_guest_consultations_after_login
from apps.notifications.constants import NotificationStatus
from apps.notifications.services.notification import NotificationService
from apps.products.services.wishlist import WishlistService
from apps.users.models import UserPhoneNumber
from apps.users.serializers.login import (
    RequestOTPSerializer,
    VerifyOTPSerializer,
)
from core_gisoo_backend.settings.components.constants import (
    GUEST_CONSULTATION_COOKIE_NAME,
    WISHLIST_COOKIE_NAME,
)
from utils.general.throttles import OTPThrottle
from drf_spectacular.utils import extend_schema

User = get_user_model()

OTP_TTL = 123
OTP_ATTEMPTS_TTL = 123
RESEND_COOLDOWN = 60
RESEND_LIMIT = 5
RESEND_WINDOW = 300


@extend_schema(
    request=RequestOTPSerializer,
    responses={200: None},
)
class RequestOTPAPIView(APIView):
    throttle_classes = [OTPThrottle]

    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]

        # TODO: enable real OTP + SMS when SMS panel is available
        # otp = str(secrets.randbelow(900000) + 100000)
        otp = "123456"
        otp_key = f"login:otp_{phone_number}"

        # notification = NotificationService.send_otp(
        #     user=None,
        #     recipient=phone_number,
        #     otp=otp,
        # )
        #
        # if notification.status != NotificationStatus.SENT:
        #     return Response(
        #         {
        #             "detail": _(
        #                 "Failed to send OTP. Please try again later."
        #             )
        #         },
        #         status=status.HTTP_503_SERVICE_UNAVAILABLE,
        #     )

        cache.set(
            otp_key,
            otp,
            timeout=OTP_TTL,
        )

        return Response(
            {
                "detail": _("OTP sent successfully."),
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(
    request=RequestOTPSerializer,
    responses={200: None},
)
class ResendOTPAPIView(APIView):
    throttle_classes = [OTPThrottle]

    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]

        timestamp_key = f"otp_timestamp_{phone_number}"
        request_count_key = f"otp_request_count_{phone_number}"

        current_timestamp = cache.get(timestamp_key)

        if current_timestamp is not None:
            raise Throttled(
                detail=_(
                    "Please wait before requesting another OTP."
                )
            )

        request_count = cache.get(request_count_key, 0)

        if request_count >= RESEND_LIMIT:
            raise Throttled(
                detail=_(
                    "Too many OTP requests. Please try again later."
                )
            )

        # TODO: enable real OTP + SMS when SMS panel is available
        # otp = str(secrets.randbelow(900000) + 100000)
        otp = "123456"
        # notification = NotificationService.send_otp(
        #     user=None,
        #     recipient=phone_number,
        #     otp=otp,
        # )
        #
        # if notification.status != NotificationStatus.SENT:
        #     return Response(
        #         {
        #             "detail": _(
        #                 "Failed to send OTP. Please try again later."
        #             )
        #         },
        #         status=status.HTTP_503_SERVICE_UNAVAILABLE,
        #     )

        otp_key = f"login:otp_{phone_number}"

        cache.set(
            otp_key,
            otp,
            timeout=OTP_TTL,
        )

        cache.set(
            timestamp_key,
            True,
            timeout=RESEND_COOLDOWN,
        )

        cache.set(
            request_count_key,
            request_count + 1,
            timeout=RESEND_WINDOW,
        )

        return Response(
            {
                "detail": _("OTP resent successfully."),
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(
    request=VerifyOTPSerializer,
    responses={200: None},
)
class VerifyOTPAPIView(APIView):

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]

        user_phone = (
            UserPhoneNumber.objects
            .filter(
                phone_number=phone_number,
                is_verified=True,
            )
            .select_related("user")
            .first()
        )

        if user_phone:
            user = user_phone.user

        else:
            user, created = User.objects.get_or_create(
                phone_number=phone_number,
            )

            user_phone, phone_created = UserPhoneNumber.objects.get_or_create(
                user=user,
                phone_number=phone_number,
                defaults={
                    "is_verified": True,
                    "is_primary": True,
                },
            )

            if not phone_created and not user_phone.is_verified:
                user_phone.is_verified = True
                user_phone.save(
                    update_fields=[
                        "is_verified",
                        "updated_at",
                    ]
                )

        if not user.is_active:
            return Response(
                {
                    "detail": _(
                        "This account is inactive."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        merge_guest_consultations_after_login(user)

        WishlistService.merge_wishlist_after_login(
            request=request,
            user=user,
        )

        cart_uuid = request.headers.get(
            "X-Cart-UUID"
        )

        _merged_cart, stock_adjustments = (
            CartService.merge_cart_after_login(
                cart_uuid=cart_uuid,
                user=user,
            )
        )

        refresh = RefreshToken.for_user(user)

        otp_key = f"login:otp_{phone_number}"
        attempts_key = f"login:otp_attempts_{phone_number}"
        timestamp_key = f"otp_timestamp_{phone_number}"
        request_count_key = f"otp_request_count_{phone_number}"

        cache.delete(otp_key)
        cache.delete(attempts_key)
        cache.delete(timestamp_key)
        cache.delete(request_count_key)

        response = Response(
            {
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "stock_adjustments": stock_adjustments,
            },
            status=status.HTTP_200_OK,
        )

        response.delete_cookie(
            GUEST_CONSULTATION_COOKIE_NAME,
        )

        response.delete_cookie(
            WISHLIST_COOKIE_NAME,
        )

        return response
