from django.db import transaction
from drf_spectacular.utils import extend_schema

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.marketing.models import MarketingSubscriber
from apps.marketing.serializers import (
    MarketingSubscribeSerializer,
    MarketingVerifyOTPSerializer,
)
from apps.marketing.services.marketing import generate_otp, save_otp, delete_otp
from apps.notifications.services.otp import get_otp


class MarketingSubscribeAPIView(APIView):

    @extend_schema(
        request=MarketingSubscribeSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                    },
                },
            },
        },
    )
    def post(self, request):
        serializer = MarketingSubscribeSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data[
            "phone_number"
        ]

        # otp = generate_otp()
        otp = "123456"
        save_otp(
            phone_number,
            otp,
        )

        return Response(
            {
                "message": "Verification code sent successfully."
            },
            status=status.HTTP_200_OK,
        )


class MarketingVerifyOTPAPIView(APIView):

    @extend_schema(
        request=MarketingVerifyOTPSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                    },
                },
            },
        },
    )
    def post(self, request):
        serializer = MarketingVerifyOTPSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data[
            "phone_number"
        ]

        otp = serializer.validated_data[
            "otp"
        ]

        saved_otp = get_otp(phone_number)

        if saved_otp is None:
            return Response(
                {
                    "detail": "OTP has expired or does not exist."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if saved_otp != otp:
            return Response(
                {
                    "detail": "Invalid OTP."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            subscriber, created = (
                MarketingSubscriber.objects.get_or_create(
                    phone_number=phone_number,
                    defaults={
                        "is_subscribed": True,
                    },
                )
            )

            if not created and not subscriber.is_subscribed:
                subscriber.is_subscribed = True
                subscriber.unsubscribed_at = None
                subscriber.save(
                    update_fields=[
                        "is_subscribed",
                        "unsubscribed_at",
                        "updated_at",
                    ]
                )

        delete_otp(phone_number)

        return Response(
            {
                "message": "You have successfully subscribed."
            },
            status=status.HTTP_200_OK,
        )
