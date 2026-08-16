from rest_framework import serializers

from apps.products.models import (
    AttributeValue,
    Product,
    ProductImage,
    ProductVariant,
    VariantAttribute, BundleItem, Bundle, ProductAttribute
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


class VariantAttributeSerializer(serializers.ModelSerializer):
    attribute = serializers.CharField(
        source="value.attribute.name"
    )

    value = serializers.CharField(
        source="value.value"
    )

    class Meta:
        model = VariantAttribute
        fields = [
            "attribute",
            "value",
        ]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = [
            "id",
            "image",
            "alt_text",
            "is_primary",
        ]


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


class SpecialOfferProductListSerializer(
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
    discount_percentage = serializers.SerializerMethodField()

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
            "discount_percentage",
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

    def get_discount_percentage(self, obj):
        variant = self._first_variant(obj)

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
            ) * 100
        )


class BundleItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(
        source="variant.product.title",
        read_only=True,
    )

    variant_sku = serializers.CharField(
        source="variant.sku",
        read_only=True,
    )

    variant_price = serializers.SerializerMethodField()

    class Meta:
        model = BundleItem
        fields = [
            "id",
            "variant",
            "variant_sku",
            "product_title",
            "quantity",
            "variant_price",
        ]

    def get_variant_price(self, obj):
        variant = obj.variant

        return (
            variant.discounted_price
            if variant.discounted_price is not None
            else variant.price
        )


class BundleSerializer(serializers.ModelSerializer):
    items = BundleItemSerializer(many=True)

    original_price = serializers.SerializerMethodField()
    discount_percent = serializers.SerializerMethodField()

    class Meta:
        model = Bundle
        fields = [
            "id",
            "title",
            "description",
            "price",
            "original_price",
            "discount_percent",
            "display_order",
            "items",
        ]

    def get_original_price(self, obj):
        total = 0

        for item in obj.items.all():
            variant = item.variant

            price = (
                variant.discounted_price
                if variant.discounted_price is not None
                else variant.price
            )

            total += price * item.quantity

        return total

    def get_discount_percent(self, obj):
        original_price = self.get_original_price(obj)

        if original_price <= 0:
            return 0

        if obj.price >= original_price:
            return 0

        return round(
            ((original_price - obj.price) / original_price) * 100
        )


class RelatedProductSerializer(serializers.ModelSerializer):
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

        if image is None:
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

        return (
            variant.discounted_price
            if variant.discounted_price is not None
            else variant.price
        )


class ProductVariantDetailSerializer(serializers.ModelSerializer):
    final_price = serializers.SerializerMethodField()
    discount_percent = serializers.SerializerMethodField()
    is_in_stock = serializers.SerializerMethodField()
    attributes = VariantAttributeSerializer(many=True)

    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "sku",
            "price",
            "discounted_price",
            "final_price",
            "discount_percent",
            "stock",
            "is_in_stock",
            "weight",
            "expiration_date",
            "attributes",
        ]

    def get_final_price(self, obj):
        return (
            obj.discounted_price
            if obj.discounted_price is not None
            else obj.price
        )

    def get_discount_percent(self, obj):
        if not obj.discounted_price or obj.price <= 0:
            return 0

        return round(
            ((obj.price - obj.discounted_price) / obj.price) * 100
        )

    def get_is_in_stock(self, obj):
        return obj.stock > 0


class ProductAttributeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        source="attribute.name"
    )

    class Meta:
        model = ProductAttribute
        fields = [
            "name",
            "value",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True)

    variants = ProductVariantDetailSerializer(
        many=True
    )

    product_attributes = ProductAttributeSerializer(
        many=True
    )

    bundles = BundleSerializer(
        many=True
    )

    related_products = serializers.SerializerMethodField()

    min_price = serializers.SerializerMethodField()
    max_price = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Product

        fields = [
            "id",
            "title",
            "slug",
            "short_description",
            "description",
            "is_available",

            "images",

            "min_price",
            "max_price",

            "variants",

            "product_attributes",

            "bundles",

            "related_products",
        ]

    def get_is_favorited(self, obj):
        request = self.context.get("request")

        if not request:
            return False

        if request.user.is_authenticated:
            return obj.wishlist_items.filter(
                wishlist__user=request.user
            ).exists()

        token = request.COOKIES.get(
            "wishlist_token"
        )

        if not token:
            return False

        return obj.wishlist_items.filter(
            wishlist__guest_token=token
        ).exists()

    def get_min_price(self, obj):
        variants = [
            variant
            for variant in obj.variants.all()
            if variant.is_active
        ]

        if not variants:
            return None

        prices = [
            (
                variant.discounted_price
                if variant.discounted_price is not None
                else variant.price
            )
            for variant in variants
        ]

        return min(prices)

    def get_max_price(self, obj):
        variants = [
            variant
            for variant in obj.variants.all()
            if variant.is_active
        ]

        if not variants:
            return None

        prices = [
            (
                variant.discounted_price
                if variant.discounted_price is not None
                else variant.price
            )
            for variant in variants
        ]

        return max(prices)

    def get_related_products(self, obj):
        products = (
            Product.objects
            .filter(
                category=obj.category,
                is_available=True,
            )
            .exclude(
                pk=obj.pk,
            )
            .select_related(
                "brand",
                "category",
            )
            .prefetch_related(
                "images",
                "variants",
            )
            .order_by("-created_at")[:4]
        )

        return RelatedProductSerializer(
            products,
            many=True,
            context=self.context,
        ).data
