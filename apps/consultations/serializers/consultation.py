import re

from rest_framework import serializers

from apps.consultations.models.consultation import (
    ConsultationRecommendation,
    ConsultationRequest,
)
from apps.products.models import HairProblem


class ConsultationOptionsSerializer(
    serializers.Serializer,
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
    serializers.ModelSerializer,
):
    class Meta:
        model = ConsultationRequest

        fields = (
            "full_name",
            "phone_number",
            "gender",
            "hair_problem",
            "duration",
            "request_phone_consultation",
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
    serializers.ModelSerializer,
):
    class Meta:
        model = ConsultationRequest

        fields = (
            "id",
            "status",
        )


class ConsultationRecommendationSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    price = serializers.SerializerMethodField()
    discounted_price = serializers.SerializerMethodField()
    discount_percent = serializers.SerializerMethodField()

    quantity = serializers.SerializerMethodField()

    class Meta:
        model = ConsultationRecommendation
        fields = (
            "id",
            "type",
            "title",
            "brand",
            "image",
            "price",
            "discounted_price",
            "discount_percent",
            "quantity",
            "explanation",
            "usage_instruction",
        )

    def get_id(self, obj):
        if obj.product_id:
            return obj.product_id

        return obj.bundle_id

    def get_type(self, obj):
        if obj.product_id:
            return "product"

        return "bundle"

    def get_title(self, obj):
        if obj.product_id:
            return obj.product.title

        return obj.bundle.title

    def get_brand(self, obj):
        if not obj.product_id:
            return None

        brand = obj.product.brand

        return str(brand) if brand else None

    def get_image(self, obj):
        if not obj.product_id:
            return None

        images = getattr(obj.product, "primary_images", [])

        if not images:
            return None

        image = images[0]

        if not image.image:
            return None

        return image.image.url

    def get_price(self, obj):
        if obj.product_id:
            variant = self._get_product_variant(obj)

            if variant is None:
                return None

            return variant.price

        bundle = obj.bundle

        return bundle.variant.price * bundle.quantity

    def get_discounted_price(self, obj):
        if obj.product_id:
            variant = self._get_product_variant(obj)

            if variant is None:
                return None

            return variant.discounted_price

        # Bundle
        bundle = obj.bundle
        original_price = bundle.variant.price * bundle.quantity

        if bundle.price < original_price:
            return bundle.price

        return None

    def get_discount_percent(self, obj):
        if obj.product_id:
            variant = self._get_product_variant(obj)

            if (
                variant is None
                or variant.discounted_price is None
                or variant.price <= 0
            ):
                return 0

            return round(
                (
                    (variant.price - variant.discounted_price)
                    / variant.price
                )
                * 100
            )

        # Bundle
        bundle = obj.bundle
        original_price = bundle.variant.price * bundle.quantity

        if original_price <= 0 or bundle.price >= original_price:
            return 0

        return round(
            (
                (original_price - bundle.price)
                / original_price
            )
            * 100
        )

    def get_quantity(self, obj):
        if obj.bundle_id:
            return obj.bundle.quantity

        return None

    def _get_product_variant(self, obj):
        variants = getattr(
            obj.product,
            "active_variants",
            [],
        )

        if variants:
            return variants[0]

        return None


class ConsultationListSerializer(
    serializers.ModelSerializer,
):
    hair_problem = serializers.CharField(
        source="hair_problem.title",
    )

    products = serializers.SerializerMethodField()

    class Meta:
        model = ConsultationRequest

        fields = (
            "id",
            "status",
            "hair_problem",
            "duration",
            "created_at",
            "updated_at",
            "products",
        )

    def get_products(self, obj):
        if obj.status != (
                ConsultationRequest.Status.COMPLETED
        ):
            return []

        return ConsultationRecommendationSerializer(
            obj.recommendations.all(),
            many=True,
            context=self.context,
        ).data


class ConsultationUpdateSerializer(
    serializers.ModelSerializer,
):
    class Meta:
        model = ConsultationRequest

        fields = (
            "full_name",
            "gender",
            "hair_problem",
            "duration",
            "request_phone_consultation",
        )

    def validate_full_name(self, value):
        value = value.strip()

        if len(value) < 3:
            raise serializers.ValidationError(
                "نام و نام خانوادگی معتبر نیست."
            )

        return value

    def validate_hair_problem(self, value):
        if not value.is_active:
            raise serializers.ValidationError(
                "این مشکل مو در حال حاضر قابل انتخاب نیست."
            )

        return value
