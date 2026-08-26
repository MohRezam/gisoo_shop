import re

from rest_framework import serializers

from apps.consultations.models.consultation import ConsultationRequest, ConsultationRecommendation
from apps.products.models import HairProblem
from apps.products.serializers import ProductListSerializer


class ConsultationOptionsSerializer(
    serializers.Serializer
):
    genders = serializers.SerializerMethodField()
    durations = serializers.SerializerMethodField()
    hair_problems = serializers.SerializerMethodField()

    def get_genders(self, obj):
        return [
            {
                "value": value,
                "label": label,
            }
            for value, label
            in ConsultationRequest.Gender.choices
        ]

    def get_durations(self, obj):
        return [
            {
                "value": value,
                "label": label,
            }
            for value, label
            in ConsultationRequest.Duration.choices
        ]

    def get_hair_problems(self, obj):
        problems = (
            HairProblem.objects
            .filter(
                is_active=True,
            )
            .order_by("created_at")
        )

        return [
            {
                "id": problem.id,
                "title": problem.title,
            }
            for problem in problems
        ]


class ConsultationCreateSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = ConsultationRequest

        fields = (
            "full_name",
            "phone_number",
            "gender",
            "hair_problem",
            "duration",
        )

    def validate_full_name(self, value):
        value = value.strip()

        if len(value) < 3:
            raise serializers.ValidationError(
                "نام و نام خانوادگی معتبر نیست."
            )

        return value

    def validate_phone_number(self, value):
        value = value.strip()

        if not re.fullmatch(
            r"09\d{9}",
            value,
        ):
            raise serializers.ValidationError(
                "شماره موبایل معتبر نیست."
            )

        return value

    def validate_hair_problem(self, value):
        if not value.is_active:
            raise serializers.ValidationError(
                "این مشکل مو در حال حاضر قابل انتخاب نیست."
            )

        return value


class ConsultationCreateResponseSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = ConsultationRequest

        fields = (
            "id",
            "status",
        )


class ConsultationListSerializer(
    serializers.ModelSerializer
):
    hair_problem = serializers.CharField(
        source="hair_problem.title",
    )

    class Meta:
        model = ConsultationRequest

        fields = (
            "id",
            "status",
            "hair_problem",
            "duration",
            "created_at",
        )


class ConsultationDetailSerializer(
    serializers.ModelSerializer
):
    hair_problem = serializers.CharField(
        source="hair_problem.title",
    )

    class Meta:
        model = ConsultationRequest

        fields = (
            "id",
            "status",
            "hair_problem",
            "duration",
            "created_at",
        )


class ConsultationRecommendationSerializer(
    serializers.ModelSerializer
):
    product = serializers.SerializerMethodField()

    class Meta:
        model = ConsultationRecommendation

        fields = (
            "product",
            "explanation",
        )

    def get_product(self, obj):
        return ProductListSerializer(
            obj.product,
            context=self.context,
        ).data


class ConsultationRecommendationsResponseSerializer(
    serializers.Serializer
):
    consultation_id = serializers.UUIDField()

    status = serializers.CharField()

    products = ConsultationRecommendationSerializer(
        many=True,
    )


class GuestOTPRequestSerializer(
    serializers.Serializer
):
    phone_number = serializers.CharField(
        max_length=20,
    )

    def validate_phone_number(self, value):
        value = value.strip()

        if not re.fullmatch(
            r"09\d{9}",
            value,
        ):
            raise serializers.ValidationError(
                "شماره موبایل معتبر نیست."
            )

        return value


class GuestOTPVerifySerializer(
    serializers.Serializer
):
    phone_number = serializers.CharField(
        max_length=20,
    )

    code = serializers.CharField(
        min_length=6,
        max_length=6,
    )

    def validate_phone_number(self, value):
        value = value.strip()

        if not re.fullmatch(
            r"09\d{9}",
            value,
        ):
            raise serializers.ValidationError(
                "شماره موبایل معتبر نیست."
            )

        return value

    def validate_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError(
                "کد تایید معتبر نیست."
            )

        return value