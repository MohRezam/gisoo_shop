from rest_framework import serializers

from apps.orders.models import Order


class CreateOrderSerializer(
    serializers.Serializer,
):
    address_id = serializers.IntegerField()

    shipping_method_id = (
        serializers.IntegerField()
    )

    description = serializers.CharField(
        required=False,
        allow_blank=True,
    )


class OrderDetailSerializer(
    serializers.ModelSerializer,
):
    items_count = serializers.SerializerMethodField()
    tracking_code = serializers.SerializerMethodField()

    class Meta:
        model = Order

        fields = [
            "id",
            "public_number",
            "status",
            "created_at",
            "total_price",
            "discount_amount",
            "items_count",
            "tracking_code",
        ]

    def get_items_count(
            self,
            obj,
    ):
        return sum(
            item.quantity
            for item in obj.items.all()
        )

    def get_tracking_code(
            self,
            obj,
    ):
        if obj.status != "shipped":
            return None

        return obj.tracking_code



class OrderListSerializer(
    serializers.ModelSerializer,
):
    order_name = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()
    status = serializers.CharField(
        source="status",
    )

    class Meta:
        model = Order

        fields = [
            "id",
            "order_name",
            "items_count",
            "status",
            "created_at",
        ]

    def get_order_name(
            self,
            obj,
    ):
        return f"سفارش #{obj.public_number}"

    def get_items_count(
            self,
            obj,
    ):
        return sum(
            item.quantity
            for item in obj.items.all()
        )