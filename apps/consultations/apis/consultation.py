from django.db.models import Prefetch
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    GenericAPIView,
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.consultations.models.consultation import ConsultationRequest
from apps.consultations.serializers import ConsultationOptionsSerializer, ConsultationCreateSerializer, \
    ConsultationCreateResponseSerializer, ConsultationListSerializer, ConsultationDetailSerializer, \
    ConsultationRecommendationsResponseSerializer, GuestOTPRequestSerializer, GuestOTPVerifySerializer
from apps.consultations.services import get_or_create_guest, get_or_create_device_access, create_guest_otp, \
    verify_guest_otp
from apps.products.models import (
    ProductImage,
    ProductVariant,
)
from utils.general.throttles import ConsultationCreateThrottle, GuestOTPRequestThrottle, GuestOTPVerifyThrottle

GUEST_ACCESS_COOKIE_NAME = (
    "consultation_guest_access"
)


class ConsultationOptionsAPIView(
    GenericAPIView
):
    permission_classes = [
        AllowAny,
    ]

    serializer_class = (
        ConsultationOptionsSerializer
    )

    @extend_schema(
        tags=["Consultations"],
        summary="Retrieve consultation options",
        responses={
            200: ConsultationOptionsSerializer,
        },
    )
    def get(
        self,
        request,
        *args,
        **kwargs,
    ):
        serializer = self.get_serializer({})

        return Response(
            serializer.data,
        )


class ConsultationCreateAPIView(
    CreateAPIView
):
    permission_classes = [
        AllowAny,
    ]

    serializer_class = (
        ConsultationCreateSerializer
    )

    throttle_classes = [
        ConsultationCreateThrottle,
    ]

    @extend_schema(
        tags=["Consultations"],
        summary="Create consultation request",
        request=ConsultationCreateSerializer,
        responses={
            201: ConsultationCreateResponseSerializer,
        },
    )
    def create(
        self,
        request,
        *args,
        **kwargs,
    ):
        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        phone_number = serializer.validated_data[
            "phone_number"
        ]

        if request.user.is_authenticated:

            active_consultation = (
                ConsultationRequest.objects
                .filter(
                    user=request.user,
                    status__in=[
                        ConsultationRequest.Status.PENDING,
                        ConsultationRequest.Status.REVIEWING,
                    ],
                )
                .first()
            )

            if active_consultation:
                return Response(
                    {
                        "detail": (
                            "شما یک درخواست مشاوره "
                            "در حال بررسی دارید."
                        ),
                        "consultation_id": (
                            active_consultation.id
                        ),
                    },
                    status=status.HTTP_409_CONFLICT,
                )

            consultation = serializer.save(
                user=request.user,
                guest=None,
            )

            response = Response(
                ConsultationCreateResponseSerializer(
                    consultation
                ).data,
                status=status.HTTP_201_CREATED,
            )

            return response

        # Guest flow

        guest = get_or_create_guest(
            phone_number,
        )

        active_consultation = (
            ConsultationRequest.objects
            .filter(
                guest=guest,
                status__in=[
                    ConsultationRequest.Status.PENDING,
                    ConsultationRequest.Status.REVIEWING,
                ],
            )
            .first()
        )

        if active_consultation:
            access = (
                get_or_create_device_access(
                    guest,
                )
            )

            response = Response(
                {
                    "detail": (
                        "شما یک درخواست مشاوره "
                        "در حال بررسی دارید."
                    ),
                    "consultation_id": (
                        active_consultation.id
                    ),
                    "status": (
                        active_consultation.status
                    ),
                },
                status=status.HTTP_409_CONFLICT,
            )

            self._set_guest_cookie(
                response,
                access.token,
            )

            return response

        consultation = serializer.save(
            guest=guest,
            user=None,
        )

        access = get_or_create_device_access(
            guest,
        )

        response = Response(
            ConsultationCreateResponseSerializer(
                consultation
            ).data,
            status=status.HTTP_201_CREATED,
        )

        self._set_guest_cookie(
            response,
            access.token,
        )

        return response

    @staticmethod
    def _set_guest_cookie(
        response,
        token,
    ):
        response.set_cookie(
            key=GUEST_ACCESS_COOKIE_NAME,
            value=token,
            max_age=60 * 60 * 24 * 365,
            httponly=True,
            secure=False,
            samesite="Lax",
        )


class ConsultationListAPIView(
    ListAPIView
):
    permission_classes = [
        AllowAny,
    ]

    serializer_class = (
        ConsultationListSerializer
    )

    def get_queryset(self):
        queryset = (
            ConsultationRequest.objects
            .select_related(
                "hair_problem",
            )
        )

        if self.request.user.is_authenticated:
            return queryset.filter(
                user=self.request.user,
            )

        token = self.request.COOKIES.get(
            GUEST_ACCESS_COOKIE_NAME
        )

        if not token:
            return queryset.none()

        return queryset.filter(
            guest__device_accesses__token=token,
        ).distinct()

    @extend_schema(
        tags=["Consultations"],
        summary="List my consultations",
        responses={
            200: ConsultationListSerializer(
                many=True
            ),
        },
    )
    def get(
        self,
        request,
        *args,
        **kwargs,
    ):
        return super().get(
            request,
            *args,
            **kwargs,
        )


class ConsultationDetailAPIView(
    RetrieveAPIView
):
    permission_classes = [
        AllowAny,
    ]

    serializer_class = (
        ConsultationDetailSerializer
    )

    def get_queryset(self):
        queryset = (
            ConsultationRequest.objects
            .select_related(
                "hair_problem",
            )
        )

        if self.request.user.is_authenticated:
            return queryset.filter(
                user=self.request.user,
            )

        token = self.request.COOKIES.get(
            GUEST_ACCESS_COOKIE_NAME
        )

        if not token:
            return queryset.none()

        return queryset.filter(
            guest__device_accesses__token=token,
        ).distinct()


class ConsultationRecommendationsAPIView(
    RetrieveAPIView
):
    permission_classes = [
        AllowAny,
    ]

    serializer_class = (
        ConsultationRecommendationsResponseSerializer
    )

    def get_queryset(self):
        queryset = (
            ConsultationRequest.objects
            .prefetch_related(
                Prefetch(
                    "recommendations__product__variants",
                    queryset=ProductVariant.objects.filter(
                        is_active=True,
                    ),
                    to_attr="active_variants",
                ),
                Prefetch(
                    "recommendations__product__images",
                    queryset=ProductImage.objects.filter(
                        is_primary=True,
                    ),
                    to_attr="primary_images",
                ),
            )
        )

        if self.request.user.is_authenticated:
            return queryset.filter(
                user=self.request.user,
            )

        token = self.request.COOKIES.get(
            GUEST_ACCESS_COOKIE_NAME
        )

        if not token:
            return queryset.none()

        return queryset.filter(
            guest__device_accesses__token=token,
        ).distinct()

    @extend_schema(
        tags=["Consultations"],
        summary="Retrieve consultation recommendations",
        responses={
            200: ConsultationRecommendationsResponseSerializer,
        },
    )
    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):
        consultation = self.get_object()

        serializer = self.get_serializer(
            {
                "consultation_id": consultation.id,
                "status": consultation.status,
                "products": consultation.recommendations.all(),
            }
        )

        return Response(
            serializer.data,
        )


class GuestOTPRequestAPIView(
    GenericAPIView
):
    permission_classes = [
        AllowAny,
    ]

    serializer_class = (
        GuestOTPRequestSerializer
    )

    throttle_classes = [
        GuestOTPRequestThrottle,
    ]

    @extend_schema(
        tags=["Consultations"],
        summary="Request guest access OTP",
        request=GuestOTPRequestSerializer,
    )
    def post(
        self,
        request,
        *args,
        **kwargs,
    ):
        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        phone_number = (
            serializer.validated_data[
                "phone_number"
            ]
        )

        guest, otp = create_guest_otp(
            phone_number,
        )

        # TODO:
        # Send otp.code using your SMS provider.
        #
        # send_otp_sms(
        #     phone_number=phone_number,
        #     code=otp.code,
        # )

        return Response(
            {
                "detail": (
                    "کد تایید ارسال شد."
                ),
            }
        )


class GuestOTPVerifyAPIView(
    GenericAPIView
):
    permission_classes = [
        AllowAny,
    ]

    serializer_class = (
        GuestOTPVerifySerializer
    )

    throttle_classes = [
        GuestOTPVerifyThrottle,
    ]

    @extend_schema(
        tags=["Consultations"],
        summary="Verify guest access OTP",
        request=GuestOTPVerifySerializer,
    )
    def post(
        self,
        request,
        *args,
        **kwargs,
    ):
        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        phone_number = (
            serializer.validated_data[
                "phone_number"
            ]
        )

        code = serializer.validated_data[
            "code"
        ]

        device_access, error = (
            verify_guest_otp(
                phone_number=phone_number,
                code=code,
            )
        )

        if error == "expired":
            return Response(
                {
                    "detail": (
                        "کد تایید منقضی شده است."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if error == "too_many_attempts":
            return Response(
                {
                    "detail": (
                        "تعداد تلاش‌ها بیش از حد مجاز است."
                    ),
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        if error:
            return Response(
                {
                    "detail": (
                        "کد تایید صحیح نیست."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = Response(
            {
                "detail": (
                    "شماره موبایل با موفقیت تایید شد."
                ),
            }
        )

        response.set_cookie(
            key=GUEST_ACCESS_COOKIE_NAME,
            value=device_access.token,
            max_age=60 * 60 * 24 * 365,
            httponly=True,
            secure=False,
            samesite="Lax",
        )

        return response