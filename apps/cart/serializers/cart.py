from rest_framework import serializers
from apps.cart.models import Cart, CartItem


class AddCartItemSerializer(serializers.Serializer):
    variant_id = serializers.IntegerField(
        min_value=1,
    )

    quantity = serializers.IntegerField(
        min_value=1,
        default=1,
    )


class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.CharField(
        source="variant.product.title"
    )

    sku = serializers.CharField(
        source="variant.sku"
    )

    price = serializers.IntegerField(
        source="variant.price"
    )

    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem

        fields = (
            "id",
            "product",
            "sku",
            "price",
            "quantity",
            "total_price",
        )

    def get_total_price(self, obj):
        return obj.variant.price * obj.quantity


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(
        many=True,
        read_only=True,
    )

    total_price = serializers.SerializerMethodField()

    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Cart

        fields = (
            "uuid",
            "total_items",
            "total_price",
            "items",
        )

    def get_total_price(self, obj):
        return sum(
            item.variant.price * item.quantity
            for item in obj.items.all()
        )

    def get_total_items(self, obj):
        return sum(
            item.quantity
            for item in obj.items.all()
        )


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(
        min_value=1,
    )
