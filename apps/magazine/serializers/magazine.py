from rest_framework import serializers

from apps.magazine.models import MagazineCategory, Magazine
from apps.products.models import Product


class MagazineCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MagazineCategory
        fields = (
            "id",
            "name",
            "slug",
        )


class RelatedProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    discounted_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "title",
            "slug",
            "image",
            "brand",
            "price",
            "discounted_price",
        )

    def get_image(self, obj):
        images = getattr(
            obj,
            "ordered_images",
            [],
        )

        if not images:
            return None

        image = images[0]

        if not image.image:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(
                image.image.url
            )

        return image.image.url

    def get_brand(self, obj):
        if not obj.brand:
            return None

        return obj.brand.title

    def get_price(self, obj):
        variants = getattr(
            obj,
            "active_variants",
            [],
        )

        if not variants:
            return None

        return variants[0].price

    def get_discounted_price(self, obj):
        variants = getattr(
            obj,
            "active_variants",
            [],
        )

        discounted_prices = [
            variant.discounted_price
            for variant in variants
            if variant.discounted_price is not None
        ]

        if not discounted_prices:
            return None

        return min(discounted_prices)


class MagazineCategorySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MagazineCategory
        fields = (
            "name",
            "slug",
        )


class RelatedMagazineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Magazine
        fields = (
            "id",
            "title",
            "slug",
            "short_description",
            "thumbnail",
            "published_at",
        )


class MagazineListSerializer(serializers.ModelSerializer):
    category = MagazineCategorySimpleSerializer(read_only=True)
    class Meta:
        model = Magazine
        fields = (
            "id",
            "title",
            "slug",
            "category",
            "thumbnail",
            "reading_time",
            "published_at",
        )

class MagazineHomePageSerializer(serializers.ModelSerializer):
    category = MagazineCategorySimpleSerializer(read_only=True)
    class Meta:
        model = Magazine
        fields = (
            "id",
            "title",
            "slug",
            "category",
            "thumbnail",
            "reading_time",
            "short_description",
            "published_at",
        )


class MagazineDetailSerializer(serializers.ModelSerializer):
    category = MagazineCategorySerializer(
        read_only=True
    )

    related_products = serializers.SerializerMethodField()
    related_articles = serializers.SerializerMethodField()

    class Meta:
        model = Magazine
        fields = (
            "id",
            "title",
            "slug",
            "short_description",
            "content",
            "thumbnail",
            "published_at",
            "category",
            "related_products",
            "related_articles",
        )

    def get_related_products(self, obj):
        products = getattr(
            obj,
            "prefetched_related_products",
            [],
        )

        return RelatedProductSerializer(
            products[:8],
            many=True,
            context=self.context,
        ).data

    def get_related_articles(self, obj):
        articles = getattr(
            obj,
            "prefetched_related_articles",
            [],
        )

        articles = [
            article
            for article in articles
            if article.pk != obj.pk
        ]

        return RelatedMagazineSerializer(
            articles[:6],
            many=True,
            context=self.context,
        ).data


class MagazineFeaturedSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(
        source="thumbnail",
    )

    class Meta:
        model = Magazine
        fields = (
            "id",
            "title",
            "slug",
            "image",
            "short_description",
            "published_at",
        )


class MagazineHomeResponseSerializer(serializers.Serializer):
    articles = MagazineListSerializer(
        many=True,
    )


class MagazineArchiveResponseSerializer(serializers.Serializer):
    categories = MagazineCategorySerializer(
        many=True,
    )

    featured_article = MagazineFeaturedSerializer(
        allow_null=True,
    )

    latest_articles = MagazineListSerializer(
        many=True,
    )


class MagazineAllResponseSerializer(serializers.Serializer):
    categories = MagazineCategorySerializer(
        many=True,
    )

    articles = serializers.JSONField()
