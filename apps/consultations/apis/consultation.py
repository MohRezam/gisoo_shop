from django.db.models import Prefetch
from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    GenericAPIView,
    ListAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from apps.consultations.models.consultation import (
    ConsultationRecommendation,
    ConsultationRequest,
)
from apps.consultations.serializers import (
    ConsultationCreateResponseSerializer,
    ConsultationCreateSerializer,
    ConsultationListSerializer,
    ConsultationOptionsSerializer,
    ConsultationRecommendationSerializer,
    ConsultationUpdateSerializer,
)
from apps.consultations.services import (
    get_guest_by_token,
    get_or_create_guest,
    merge_guest_consultations_after_login, create_guest_device_access,
)
from apps.products.models import ProductImage
from core_gisoo_backend.settings.components.constants import GUEST_CONSULTATION_COOKIE_NAME
from utils.general.throttles import ConsultationCreateThrottle


class ConsultationOptionsAPIView(
    GenericAPIView,
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
    CreateAPIView,
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

            data["phone_number"] = (
                request.user.phone_number
            )

            profile_name = " ".join(
                part
                for part in [
                    (
                        request.user.first_name
                        or ""
                    ).strip(),
                    (
                        request.user.last_name
                        or ""
                    ).strip(),
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

        phone_number = (
            serializer.validated_data[
                "phone_number"
            ]
        )

        if request.user.is_authenticated:
            active_consultation = (
                ConsultationRequest.objects
                .filter(
                    user=request.user,
                    status=(
                        ConsultationRequest.Status.PENDING
                    ),
                )
                .first()
            )

        else:
            active_consultation = (
                ConsultationRequest.objects
                .filter(
                    phone_number=phone_number,
                    status=(
                        ConsultationRequest.Status.PENDING
                    ),
                )
                .first()
            )

        if active_consultation:
            return Response(
                {
                    "detail": (
                        "شما یک درخواست مشاوره "
                        "در انتظار دارید."
                    ),
                    "status": (
                        active_consultation.status
                    ),
                    "id": active_consultation.id,
                },
                status=status.HTTP_409_CONFLICT,
            )

        if request.user.is_authenticated:
            consultation = serializer.save(
                user=request.user,
                guest=None,
                phone_number=(
                    request.user.phone_number
                ),
            )

            return Response(
                ConsultationCreateResponseSerializer(
                    consultation,
                    context={
                        "request": request,
                    },
                ).data,
                status=status.HTTP_201_CREATED,
            )

        # -----------------------------------------
        # GUEST
        # -----------------------------------------

        guest = get_or_create_guest(
            phone_number,
        )

        consultation = serializer.save(
            guest=guest,
            user=None,

            # Guests MUST always have
            # phone consultation.
            request_phone_consultation=True,
        )

        guest_access = (
            create_guest_device_access(
                guest,
            )
        )

        response = Response(
            ConsultationCreateResponseSerializer(
                consultation,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_201_CREATED,
        )

        response.set_cookie(
            key=GUEST_CONSULTATION_COOKIE_NAME,
            value=guest_access.token,
            max_age=30 * 24 * 60 * 60,
            httponly=True,
            secure=False,
            samesite="Lax",
        )

        return response

class ConsultationListAPIView(
    ListAPIView,
):
    permission_classes = [
        # We manually use authentication here
        # because guests do not have a /my/ page.
        AllowAny,
    ]

    serializer_class = (
        ConsultationListSerializer
    )

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return ConsultationRequest.objects.none()

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
                    queryset=(
                        ProductImage.objects.filter(
                            is_primary=True,
                        )
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
        summary=(
            "List my consultations "
            "with product suggestions"
        ),
        responses={
            200: ConsultationListSerializer(
                many=True,
            ),
        },
    )
    def get(
        self,
        request,
        *args,
        **kwargs,
    ):
        if not request.user.is_authenticated:
            return Response(
                {
                    "detail": (
                        "احراز هویت الزامی است."
                    )
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return super().get(
            request,
            *args,
            **kwargs,
        )


class ConsultationUpdateAPIView(
    RetrieveUpdateAPIView,
):
    permission_classes = [
        AllowAny,
    ]

    serializer_class = (
        ConsultationUpdateSerializer
    )

    def get_object(self):
        consultation_id = self.kwargs["pk"]

        queryset = (
            ConsultationRequest.objects
            .select_related(
                "user",
                "guest",
                "hair_problem",
            )
        )

        consultation = (
            queryset
            .filter(
                id=consultation_id,
            )
            .first()
        )

        if consultation is None:
            from rest_framework.exceptions import NotFound

            raise NotFound(
                "درخواست مشاوره پیدا نشد."
            )

        # -----------------------------------------
        # AUTHENTICATED USER
        # -----------------------------------------

        if self.request.user.is_authenticated:
            if consultation.user_id != (
                    self.request.user.id
            ):
                from rest_framework.exceptions import (
                    PermissionDenied,
                )

                raise PermissionDenied(
                    "شما به این درخواست مشاوره "
                    "دسترسی ندارید."
                )

            return consultation

        # -----------------------------------------
        # GUEST
        # -----------------------------------------

        guest_token = self.request.COOKIES.get(
            GUEST_CONSULTATION_COOKIE_NAME,
        )

        if not guest_token:
            from rest_framework.exceptions import (
                NotAuthenticated,
            )

            raise NotAuthenticated(
                "Guest access token الزامی است."
            )

        guest = get_guest_by_token(
            guest_token,
        )

        if guest is None:
            from rest_framework.exceptions import (
                NotAuthenticated,
            )

            raise NotAuthenticated(
                "Guest access token معتبر نیست."
            )

        if consultation.guest_id != guest.id:
            from rest_framework.exceptions import (
                PermissionDenied,
            )

            raise PermissionDenied(
                "شما به این درخواست مشاوره "
                "دسترسی ندارید."
            )

        return consultation

    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):
        consultation = self.get_object()

        return Response(
            {
                "id": consultation.id,
                "full_name": consultation.full_name,
                "phone_number": (
                    consultation.phone_number
                ),
                "gender": consultation.gender,
                "hair_problem": (
                    consultation.hair_problem_id
                ),
                "duration": consultation.duration,
                "status": consultation.status,
                "request_phone_consultation": (
                    consultation.request_phone_consultation
                ),
                "created_at": consultation.created_at,
                "updated_at": consultation.updated_at,
            }
        )

    def update(
        self,
        request,
        *args,
        **kwargs,
    ):
        consultation = self.get_object()

        # Only PENDING consultations are editable.
        if consultation.status != (
            ConsultationRequest.Status.PENDING
        ):
            return Response(
                {
                    "detail": (
                        "این درخواست دیگر "
                        "قابل ویرایش نیست."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        data = request.data.copy()

        # -----------------------------------------
        # GUEST
        # -----------------------------------------

        if not request.user.is_authenticated:
            # Guest can never disable
            # phone consultation.
            data[
                "request_phone_consultation"
            ] = True

        serializer = self.get_serializer(
            consultation,
            data=data,
            partial=kwargs.get("partial", False),
        )

        serializer.is_valid(
            raise_exception=True,
        )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )