from rest_framework import serializers

from apps.products.models import (
    AttributeValue,
    Brand,
    Category,
    Product,
    ProductImage,
    ProductVariant,
    VariantAttribute, BundleItem, Bundle, HairProblem,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category

        fields = (
            "id",
            "title",
            "slug",
            "parent",
        )


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand

        fields = (
            "id",
            "title",
            "slug",
            "logo",
        )


class AttributeValueSerializer(
    serializers.ModelSerializer,
):
    attribute = serializers.CharField(
        source="attribute.name",
    )

    class Meta:
        model = AttributeValue

        fields = (
            "attribute",
            "value",
        )


class VariantAttributeSerializer(
    serializers.ModelSerializer,
):
    attribute = serializers.CharField(
        source="value.attribute.name",
    )

    value = serializers.CharField(
        source="value.value",
    )

    class Meta:
        model = VariantAttribute

        fields = (
            "attribute",
            "value",
        )


class ProductImageSerializer(
    serializers.ModelSerializer,
):
    class Meta:
        model = ProductImage

        fields = (
            "id",
            "image",
            "alt_text",
        )


class ProductVariantSerializer(
    serializers.ModelSerializer,
):
    attributes = VariantAttributeSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = ProductVariant

        fields = (
            "id",
            "sku",
            "price",
            "discounted_price",
            "stock",
            "is_active",
            "attributes",
        )


class ProductListSerializer(
    serializers.ModelSerializer,
):
    brand = serializers.StringRelatedField()

    category = serializers.StringRelatedField()

    thumbnail = serializers.SerializerMethodField()

    price = serializers.SerializerMethodField()

    discounted_price = (
        serializers.SerializerMethodField()
    )

    has_discount = (
        serializers.SerializerMethodField()
    )

    stock = serializers.SerializerMethodField()

    class Meta:
        model = Product

        fields = (
            "id",
            "title",
            "slug",
            "brand",
            "category",
            "thumbnail",
            "price",
            "discounted_price",
            "has_discount",
            "stock",
            "is_available",
        )

    def _first_variant(
            self,
            obj,
    ):
        variants = getattr(
            obj,
            "active_variants",
            [],
        )

        if variants:
            return variants[0]

        return None

    def get_thumbnail(
            self,
            obj,
    ):
        images = getattr(
            obj,
            "primary_images",
            [],
        )

        if images:
            return images[0].image.url

        return None

    def get_price(
            self,
            obj,
    ):
        variant = self._first_variant(
            obj,
        )

        if variant is None:
            return None

        return variant.price

    def get_discounted_price(
            self,
            obj,
    ):
        variant = self._first_variant(
            obj,
        )

        if variant is None:
            return None

        return variant.discounted_price

    def get_has_discount(
            self,
            obj,
    ):
        variant = self._first_variant(
            obj,
        )

        if variant is None:
            return False

        return (
                variant.discounted_price
                is not None
        )

    def get_stock(
            self,
            obj,
    ):
        variant = self._first_variant(
            obj,
        )

        if variant is None:
            return 0

        return variant.stock


class BundleItemSerializer(serializers.ModelSerializer):
    variant_id = serializers.IntegerField(
        source="variant.id",
        read_only=True,
    )

    sku = serializers.CharField(
        source="variant.sku",
        read_only=True,
    )

    class Meta:
        model = BundleItem

        fields = [
            "variant_id",
            "sku",
            "quantity",
        ]


class BundleSerializer(serializers.ModelSerializer):
    items = BundleItemSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Bundle

        fields = [
            "id",
            "title",
            "description",
            "price",
            "items",
        ]


class ProductDetailSerializer(
    serializers.ModelSerializer,
):
    brand = serializers.StringRelatedField()

    category = serializers.StringRelatedField()

    images = ProductImageSerializer(
        many=True,
        read_only=True,
    )

    variants = ProductVariantSerializer(
        many=True,
        read_only=True,
    )

    bundles = BundleSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Product

        fields = (
            "id",
            "title",
            "slug",
            "short_description",
            "description",
            "brand",
            "category",
            "images",
            "variants",
            "bundles"
        )

class HairProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = HairProblem
        fields = (
            "id",
            "title",
            "slug",
            "is_active"
        )