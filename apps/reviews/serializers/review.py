from rest_framework import serializers

from apps.reviews.models.review import ProductReview, review_author_label


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
        return review_author_label(obj)


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
        return review_author_label(obj)


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
        return review_author_label(obj)
