from django.db.models import Prefetch

from rest_framework.generics import (
    CreateAPIView,
    GenericAPIView,
    RetrieveAPIView,
)
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from apps.consultations.models.consultation import ConsultationRequest
from apps.consultations.serializers import ConsultationOptionsSerializer, ConsultationCreateSerializer, \
    ConsultationCreateResponseSerializer, ConsultationDetailSerializer, ConsultationRecommendationsResponseSerializer
from apps.products.models import (
    ProductImage,
    ProductVariant,
)


class ConsultationOptionsAPIView(
    GenericAPIView,
):
    serializer_class = ConsultationOptionsSerializer

    @extend_schema(
        tags=["Consultations"],
        summary="Retrieve Consultation Options",
        responses={
            200: ConsultationOptionsSerializer,
        },
    )
    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer({})

        return Response(serializer.data)


class ConsultationCreateAPIView(
    CreateAPIView,
):
    queryset = ConsultationRequest.objects.all()

    serializer_class = ConsultationCreateSerializer

    @extend_schema(
        tags=["Consultations"],
        summary="Create Consultation Request",
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

        consultation = serializer.save()

        response_serializer = (
            ConsultationCreateResponseSerializer(
                consultation,
            )
        )

        return Response(
            response_serializer.data,
            status=201,
        )


class ConsultationDetailAPIView(
    RetrieveAPIView,
):
    queryset = (
        ConsultationRequest.objects
        .select_related(
            "hair_problem",
        )
    )

    serializer_class = ConsultationDetailSerializer

    @extend_schema(
        tags=["Consultations"],
        summary="Retrieve Consultation",
        responses={
            200: ConsultationDetailSerializer,
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


class ConsultationRecommendationsAPIView(
    RetrieveAPIView,
):
    serializer_class = (
        ConsultationRecommendationsResponseSerializer
    )

    queryset = (
        ConsultationRequest.objects
        .select_related(
            "hair_problem",
        )
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

    @extend_schema(
        tags=["Consultations"],
        summary="Retrieve Consultation Recommendations",
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

        return Response(serializer.data)
