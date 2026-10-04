from rest_framework import serializers

from apps.reviews.models import ProductReview


class ProductReviewSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = ProductReview
        fields = (
            "id",
            "product",
            "rating",
            "comment",
            "status",
            "created_at",
            "updated_at",
            "author_name",
        )
        read_only_fields = (
            "id",
            "product",
            "status",
            "created_at",
            "updated_at",
            "author_name",
        )

    def get_author_name(self, obj):
        user = obj.user

        full_name = " ".join(
            part
            for part in (
                user.first_name,
                user.last_name,
            )
            if part
        ).strip()

        if full_name:
            return full_name

        phone = user.phone_number

        if len(phone) <= 7:
            return "*" * len(phone)

        return (
            phone[:4]
            + "*" * (len(phone) - 8)
            + phone[-4:]
        )


class ProductReviewPublicSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = ProductReview

        fields = (
            "id",
            "rating",
            "comment",
            "created_at",
            "author_name",
        )

        read_only_fields = fields

    def get_author_name(self, obj):
        user = obj.user

        full_name = " ".join(
            part
            for part in [
                user.first_name,
                user.last_name,
            ]
            if part
        ).strip()

        if full_name:
            return full_name

        phone = user.phone_number

        if len(phone) <= 7:
            return "*" * len(phone)

        return (
                phone[:4]
                + "*" * (len(phone) - 8)
                + phone[-4:]
        )


class HomepageReviewSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    product_title = serializers.CharField(
        source="product.title",
        read_only=True,
    )

    product_slug = serializers.CharField(
        source="product.slug",
        read_only=True,
    )

    class Meta:
        model = ProductReview

        fields = (
            "id",
            "rating",
            "comment",
            "created_at",
            "author_name",
            "product_title",
            "product_slug",
        )

        read_only_fields = fields

    def get_author_name(self, obj):
        user = obj.user

        full_name = " ".join(
            part
            for part in [
                user.first_name,
                user.last_name,
            ]
            if part
        ).strip()

        if full_name:
            return full_name

        phone = user.phone_number

        if len(phone) <= 7:
            return "*" * len(phone)

        return (
                phone[:4]
                + "*" * (len(phone) - 8)
                + phone[-4:]
        )
