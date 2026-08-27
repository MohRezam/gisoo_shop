import re

from rest_framework import serializers

from apps.consultations.models.consultation import (
    ConsultationRequest,
    ConsultationRecommendation,
)
from apps.products.models import HairProblem


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
                "label": str(label),
            }
            for value, label
            in ConsultationRequest.Gender.choices
        ]

    def get_durations(self, obj):
        return [
            {
                "value": value,
                "label": str(label),
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
            "status",
        )


class ConsultationRecommendationSerializer(
    serializers.ModelSerializer
):
    title = serializers.CharField(
        source="product.title",
    )
    brand = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = ConsultationRecommendation

        fields = (
            "title",
            "brand",
            "image",
            "explanation",
        )

    def get_brand(self, obj):
        brand = obj.product.brand

        if not brand:
            return None

        return str(brand)

    def get_image(self, obj):
        product = obj.product
        images = getattr(
            product,
            "primary_images",
            None,
        )

        if images:
            image = images[0]
            if image.image:
                return image.image.url
            return None

        image = (
            product.images
            .filter(is_primary=True)
            .first()
        )

        if image and image.image:
            return image.image.url

        return None


class ConsultationListSerializer(
    serializers.ModelSerializer
):
    hair_problem = serializers.CharField(
        source="hair_problem.title",
    )
    products = serializers.SerializerMethodField()

    class Meta:
        model = ConsultationRequest

        fields = (
            "status",
            "hair_problem",
            "duration",
            "created_at",
            "products",
        )

    def get_products(self, obj):
        if obj.status not in [
            ConsultationRequest.Status.REVIEWING,
            ConsultationRequest.Status.COMPLETED,
        ]:
            return []

        return ConsultationRecommendationSerializer(
            obj.recommendations.all(),
            many=True,
            context=self.context,
        ).data
