from rest_framework import serializers

from apps.cart.models import Cart, CartItem
from apps.cart.services import calculate_cart_totals


class AddCartItemSerializer(serializers.Serializer):
    variant_id = serializers.IntegerField(
        min_value=1,
        required=False,
    )

    bundle_id = serializers.IntegerField(
        min_value=1,
        required=False,
    )

    quantity = serializers.IntegerField(
        min_value=1,
        default=1,
    )

    def validate(self, attrs):
        variant_id = attrs.get("variant_id")
        bundle_id = attrs.get("bundle_id")

        if (variant_id is None) == (bundle_id is None):
            raise serializers.ValidationError(
                "Provide either variant_id or bundle_id."
            )

        return attrs


class CartItemSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    sku = serializers.SerializerMethodField()

    price = serializers.SerializerMethodField()
    discounted_price = serializers.SerializerMethodField()
    discount_percent = serializers.SerializerMethodField()

    bundle_quantity = serializers.SerializerMethodField()
    unit_price = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem

        fields = (
            "id",
            "type",
            "title",
            "sku",
            "price",
            "discounted_price",
            "discount_percent",
            "quantity",
            "bundle_quantity",
            "unit_price",
            "total_price",
        )

    def get_type(self, obj):
        if obj.bundle_id:
            return "bundle"

        return "product"

    def get_title(self, obj):
        if obj.bundle_id:
            return obj.bundle.title

        return obj.variant.product.title

    def get_sku(self, obj):
        if obj.bundle_id:
            return obj.bundle.variant.sku

        return obj.variant.sku

    def get_price(self, obj):
        if obj.bundle_id:
            return (
                    obj.bundle.variant.price
                    * obj.bundle.quantity
            )

        return obj.variant.price

    def get_discounted_price(self, obj):
        if obj.bundle_id:
            original_price = (
                    obj.bundle.variant.price
                    * obj.bundle.quantity
            )

            if obj.bundle.price < original_price:
                return obj.bundle.price

            return None

        return obj.variant.discounted_price

    def get_discount_percent(self, obj):
        price = self.get_price(obj)
        discounted_price = self.get_discounted_price(obj)

        if discounted_price is None or price <= 0:
            return 0

        return round(
            (
                    (price - discounted_price)
                    / price
            ) * 100
        )

    def get_bundle_quantity(self, obj):
        if obj.bundle_id:
            return obj.bundle.quantity

        return None

    def get_unit_price(self, obj):
        discounted_price = self.get_discounted_price(obj)

        if discounted_price is not None:
            return discounted_price

        return self.get_price(obj)

    def get_total_price(self, obj):
        return self.get_unit_price(obj) * obj.quantity


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(
        many=True,
        read_only=True,
    )

    original_subtotal = serializers.SerializerMethodField()
    product_discount = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    coupon_discount = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()

    total_items = serializers.SerializerMethodField()
    total_products = serializers.SerializerMethodField()

    class Meta:
        model = Cart

        fields = (
            "uuid",
            "total_items",
            "total_products",
            "original_subtotal",
            "product_discount",
            "subtotal",
            "coupon_discount",
            "total_price",
            "discount",
            "items",
        )

    def get_totals(self, obj):
        if hasattr(self, "_cart_totals"):
            return self._cart_totals

        request = self.context.get("request")

        user = (
            request.user
            if request
            else None
        )

        self._cart_totals = calculate_cart_totals(
            cart=obj,
            user=user,
            discount=obj.discount,
        )

        return self._cart_totals

    def get_original_subtotal(self, obj):
        return self.get_totals(obj)["original_subtotal"]

    def get_product_discount(self, obj):
        return self.get_totals(obj)["product_discount"]

    def get_subtotal(self, obj):
        return self.get_totals(obj)["subtotal"]

    def get_coupon_discount(self, obj):
        return self.get_totals(obj)["coupon_discount"]

    def get_total_price(self, obj):
        return self.get_totals(obj)["total"]

    def get_discount(self, obj):
        if obj.discount_id:
            return obj.discount.code

        return None

    def get_total_items(self, obj):
        return sum(
            item.quantity
            for item in obj.items.all()
        )

    def get_total_products(self, obj):
        total = 0

        for item in obj.items.all():
            if item.bundle_id:
                total += (
                        item.quantity
                        * item.bundle.quantity
                )
            else:
                total += item.quantity

        return total


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(
        min_value=1,
    )


class ApplyDiscountSerializer(serializers.Serializer):
    code = serializers.CharField(
        max_length=50,
        trim_whitespace=True,
    )
