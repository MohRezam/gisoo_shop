from rest_framework import serializers

from apps.cart.models import Cart, CartItem


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
            )
            * 100
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

    subtotal = serializers.SerializerMethodField()
    total_discount = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()
    total_products = serializers.SerializerMethodField()

    class Meta:
        model = Cart

        fields = (
            "uuid",
            "total_items",
            "total_products",
            "subtotal",
            "total_discount",
            "total_price",
            "items",
        )

    def get_subtotal(self, obj):
        total = 0

        for item in obj.items.all():
            if item.bundle_id:
                price = (
                    item.bundle.variant.price
                    * item.bundle.quantity
                )
            else:
                price = item.variant.price

            total += price * item.quantity

        return total

    def get_total_discount(self, obj):
        total_discount = 0

        for item in obj.items.all():
            if item.bundle_id:
                original_price = (
                    item.bundle.variant.price
                    * item.bundle.quantity
                )

                final_price = item.bundle.price

                if final_price >= original_price:
                    final_price = original_price

            else:
                original_price = item.variant.price

                final_price = (
                    item.variant.discounted_price
                    if item.variant.discounted_price is not None
                    else item.variant.price
                )

            total_discount += (
                original_price - final_price
            ) * item.quantity

        return total_discount

    def get_total_price(self, obj):
        return (
            self.get_subtotal(obj)
            - self.get_total_discount(obj)
        )

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