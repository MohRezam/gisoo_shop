import re

from rest_framework import serializers

from apps.consultations.models.consultation import (
    ConsultationRecommendation,
    ConsultationRecommendationPack,
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
            .order_by("display_order", "title")
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
    type = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    product_id = serializers.SerializerMethodField()

    price = serializers.SerializerMethodField()
    discounted_price = serializers.SerializerMethodField()
    discount_percent = serializers.SerializerMethodField()

    quantity = serializers.SerializerMethodField()

    class Meta:
        model = ConsultationRecommendation
        fields = (
            "id",
            "type",
            "product_id",
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

    def get_type(self, obj):
        return "product"

    def get_product_id(self, obj):
        return obj.variant.product_id

    def get_title(self, obj):
        return obj.variant.product.title

    def get_brand(self, obj):
        brand = obj.variant.product.brand

        return str(brand) if brand else None

    def get_image(self, obj):
        product = obj.variant.product

        images = getattr(product, "primary_images", None)
        if images is None:
            images = product.images.filter(is_primary=True)

        image = images[0] if images else None

        if not image or not image.image:
            return None

        return image.image.url

    def get_price(self, obj):
        return obj.variant.price

    def get_discounted_price(self, obj):
        return obj.variant.discounted_price

    def get_discount_percent(self, obj):
        price = self.get_price(obj)
        discounted_price = self.get_discounted_price(obj)

        if (
            discounted_price is None
            or price <= 0
        ):
            return 0

        return round(
            (
                (price - discounted_price)
                / price
            ) * 100
        )

    def get_quantity(self, obj):
        return 1


class ConsultationRecommendationPackSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    class Meta:
        model = ConsultationRecommendationPack
        fields = (
            "id",
            "title",
            "description",
            "display_order",
            "products",
        )

    def get_products(self, obj):
        recommendations = [
            item.recommendation
            for item in obj.items.all()
            if item.recommendation_id
        ]
        return ConsultationRecommendationSerializer(
            recommendations,
            many=True,
            context=self.context,
        ).data


class ConsultationListSerializer(
    serializers.ModelSerializer,
):
    hair_problem = serializers.CharField(
        source="hair_problem.title",
    )

    products = serializers.SerializerMethodField()
    recommendation_packs = serializers.SerializerMethodField()

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
            "recommendation_packs",
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

    def get_recommendation_packs(self, obj):
        if obj.status != (
                ConsultationRequest.Status.COMPLETED
        ):
            return []

        packs = [
            pack
            for pack in obj.recommendation_packs.all()
            if len(pack.items.all()) > 0
        ]
        return ConsultationRecommendationPackSerializer(
            packs,
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


class AddSelectedRecommendationsSerializer(
    serializers.Serializer
):
    recommendation_ids = serializers.ListField(
        child=serializers.IntegerField(
            min_value=1,
        ),
        allow_empty=False,
    )
