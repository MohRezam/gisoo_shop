from django.db.models import Prefetch

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    GenericAPIView,
    ListAPIView,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response

from apps.consultations.models.consultation import (
    ConsultationRecommendation,
    ConsultationRequest,
)
from apps.consultations.serializers import (
    ConsultationOptionsSerializer,
    ConsultationCreateSerializer,
    ConsultationCreateResponseSerializer,
    ConsultationListSerializer,
)
from apps.consultations.services import (
    get_or_create_guest,
    merge_guest_consultations_after_login,
)
from apps.products.models import ProductImage
from utils.general.throttles import ConsultationCreateThrottle


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
        data = request.data.copy()

        if request.user.is_authenticated:
            merge_guest_consultations_after_login(
                request.user,
            )

            # Ownership and contact info always come from JWT account.
            data["phone_number"] = (
                request.user.phone_number
            )

            profile_name = " ".join(
                part
                for part in [
                    (request.user.first_name or "").strip(),
                    (request.user.last_name or "").strip(),
                ]
                if part
            )

            if profile_name:
                data["full_name"] = profile_name

        serializer = self.get_serializer(
            data=data,
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
        else:
            active_consultation = (
                ConsultationRequest.objects
                .filter(
                    phone_number=phone_number,
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
                    "status": (
                        active_consultation.status
                    ),
                },
                status=status.HTTP_409_CONFLICT,
            )

        if request.user.is_authenticated:
            consultation = serializer.save(
                user=request.user,
                guest=None,
                phone_number=request.user.phone_number,
            )
        else:
            guest = get_or_create_guest(
                phone_number,
            )

            consultation = serializer.save(
                guest=guest,
                user=None,
            )

        return Response(
            ConsultationCreateResponseSerializer(
                consultation
            ).data,
            status=status.HTTP_201_CREATED,
        )


class ConsultationListAPIView(
    ListAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = (
        ConsultationListSerializer
    )

    def get_queryset(self):
        merge_guest_consultations_after_login(
            self.request.user,
        )

        recommendations_qs = (
            ConsultationRecommendation.objects
            .select_related(
                "product",
                "product__brand",
            )
            .prefetch_related(
                Prefetch(
                    "product__images",
                    queryset=ProductImage.objects.filter(
                        is_primary=True,
                    ),
                    to_attr="primary_images",
                ),
            )
        )

        return (
            ConsultationRequest.objects
            .select_related(
                "hair_problem",
            )
            .prefetch_related(
                Prefetch(
                    "recommendations",
                    queryset=recommendations_qs,
                ),
            )
            .filter(
                user=self.request.user,
            )
        )

    @extend_schema(
        tags=["Consultations"],
        summary="List my consultations with product suggestions",
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
