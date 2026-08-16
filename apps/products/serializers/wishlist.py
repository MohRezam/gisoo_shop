from rest_framework import serializers

from apps.products.models import (
    Product,
    WishlistItem,
)


class WishlistProductSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "thumbnail",
            "price",
        ]

    def get_thumbnail(self, obj):
        image = next(
            (
                image
                for image in obj.images.all()
                if image.is_primary
            ),
            None,
        )

        if image is None:
            image = obj.images.first()

        if image is None or not image.image:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(
                image.image.url
            )

        return image.image.url

    def get_price(self, obj):
        variant = next(
            (
                variant
                for variant in obj.variants.all()
                if variant.is_active
            ),
            None,
        )

        if variant is None:
            return None

        if variant.discounted_price is not None:
            return variant.discounted_price

        return variant.price


class WishlistItemSerializer(serializers.ModelSerializer):
    product = WishlistProductSerializer(
        read_only=True
    )

    class Meta:
        model = WishlistItem
        fields = [
            "id",
            "product",
            "created_at",
        ]


class WishlistSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    items = WishlistItemSerializer(many=True)
