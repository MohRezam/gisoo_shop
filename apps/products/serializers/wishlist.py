from rest_framework import serializers

from apps.products.models import (
    Product,
    WishlistItem,
)


class WishlistProductSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    is_in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "thumbnail",
            "price",
            "is_in_stock"
        ]

    def get_is_in_stock(self, obj):
        return any(
            variant.stock > 0
            for variant in obj.variants.all()
        )

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
    items = WishlistItemSerializer(
        many=True
    )


class WishlistToggleSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(
            is_available=True,
        ),
        help_text=(
            "ID of the product to add to or "
            "remove from the wishlist."
        ),
    )


class WishlistToggleResponseSerializer(serializers.Serializer):
    is_favorited = serializers.BooleanField(
        help_text=(
            "Whether the product is currently "
            "in the wishlist."
        ),
    )

    action = serializers.ChoiceField(
        choices=[
            ("added", "Added"),
            ("removed", "Removed"),
        ],
        help_text=(
            "Action performed on the wishlist."
        ),
    )


class WishlistDeleteResponseSerializer(serializers.Serializer):
    detail = serializers.CharField(
        help_text="Confirmation message.",
    )

    product_id = serializers.IntegerField(
        help_text="ID of the removed product.",
    )

    is_favorited = serializers.BooleanField(
        help_text="Always false after successful removal.",
    )
