from rest_framework import serializers

from apps.orders.models import Order
from apps.payments.models import Payment
from apps.payments.serializers.payment_intent import PaymentIntentSerializer


class CreateOrderSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()
    shipping_method_id = serializers.IntegerField()
    description = serializers.CharField(
        required=False,
        allow_blank=True,
    )


class OrderPaymentSerializer(
    serializers.ModelSerializer,
):
    class Meta:
        model = Payment

        fields = [
            "id",
            "amount",
            "status",
            "gateway_payment_id",
            "gateway_reference_id",
            "paid_at",
        ]


class OrderListSerializer(serializers.ModelSerializer):
    payment_intent = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "public_number",
            "status",
            "products_price",
            "shipping_price",
            "discount_amount",
            "total_price",
            "expires_at",
            "tracking_code",
            "payment_intent",
            "created_at",
        ]

    def get_payment_intent(self, obj):
        intent = None
        intents = getattr(obj, "_prefetched_objects_cache", {}).get("payment_intents")
        if intents is not None:
            intent = intents[0] if intents else None
        else:
            intent = obj.payment_intents.select_related("destination_card").order_by(
                "-created_at"
            ).first()
        if intent is None:
            return None
        return PaymentIntentSerializer(intent, context=self.context).data


class OrderDetailSerializer(
    serializers.ModelSerializer,
):
    payment = OrderPaymentSerializer(
        read_only=True,
    )
    payment_intent = serializers.SerializerMethodField()
    shipping_method_title = serializers.CharField(
        source="shipping_method.title",
        read_only=True,
    )

    name = serializers.CharField(
        source="product_title",
        read_only=True,
    )

    image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "product_id",
            "name",
            "image",
            "quantity",
            "original_unit_price",
            "unit_price",
            "total_price",
        ]
        read_only_fields = fields

    def get_image(self, obj):
        request = self.context.get("request")

        image = next(
            (
                product_image
                for product_image in obj.variant.product.images.all()
                if product_image.is_primary and product_image.image
            ),
            None,
        )

        if image is None:
            return None

        image_url = image.image.url

        if request is not None:
            return request.build_absolute_uri(
                image_url
            )

        return image_url


class OrderBundleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderBundle
        fields = [
            "id",
            "title",
            "quantity",
            "unit_price",
            "total_price",
        ]
        read_only_fields = fields


class OrderListSerializer(serializers.ModelSerializer):
    order_name = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    bundles = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "order_name",
            "status",
            "created_at",
            "items_count",
            "items",
            "bundles",
        ]
        read_only_fields = fields

    def get_order_name(self, obj):
        return f"سفارش #{obj.id}"

    def get_items_count(self, obj):
        return sum(
            item.quantity
            for item in obj.items.all()
        )

    def get_items(self, obj):
        return OrderItemListSerializer(
            obj.items.all(),
            many=True,
            context=self.context,
        ).data

    def get_bundles(self, obj):
        return OrderBundleListSerializer(
            obj.bundles.all(),
            many=True,
            context=self.context,
        ).data


class OrderDetailSerializer(serializers.ModelSerializer):
    items_count = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    bundles = serializers.SerializerMethodField()
    tracking_code = serializers.SerializerMethodField()
    payment_intent = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "public_number",
            "status",
            "products_price",
            "shipping_price",
            "discount_amount",
            "total_price",
            "expires_at",
            "phone_number",
            "province",
            "city",
            "postal_code",
            "address",
            "description",
            "tracking_code",
            "shipping_method_title",
            "payment",
            "payment_intent",
            "created_at",
        ]

    def get_payment_intent(self, obj):
        intent = obj.payment_intents.select_related("destination_card").order_by(
            "-created_at"
        ).first()
        if intent is None:
            return None
        return PaymentIntentSerializer(intent, context=self.context).data


class TrackOrderQuerySerializer(serializers.Serializer):
    code = serializers.CharField()
    phone = serializers.CharField(max_length=11)
