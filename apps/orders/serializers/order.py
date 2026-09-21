from rest_framework import serializers

from apps.orders.models import (
    Order,
    OrderBundle,
    OrderItem,
    OrderStatus,
)
from apps.payments.models import PaymentIntentStatus
from apps.payments.services.submit_receipt import (
    ALLOWED_STATUSES as RECEIPT_UPLOAD_STATUSES,
)


class CreateOrderSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()
    shipping_method_id = serializers.IntegerField()
    description = serializers.CharField(
        required=False,
        allow_blank=True,
    )


class OrderItemListSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(
        source="variant.product.id",
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
    payment_intent = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "public_number",
            "order_name",
            "status",
            "total_price",
            "created_at",
            "items_count",
            "items",
            "bundles",
            "payment_intent",
        ]
        read_only_fields = fields

    def get_order_name(self, obj):
        if obj.public_number:
            return f"سفارش {obj.public_number}"
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

    def get_payment_intent(self, obj):
        return OrderDetailSerializer.get_payment_intent(self, obj)


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
            "created_at",
            "products_price",
            "shipping_price",
            "total_price",
            "discount_amount",
            "items_count",
            "items",
            "bundles",
            "tracking_code",
            "payment_intent",
            "phone_number",
            "province",
            "city",
            "address",
        ]
        read_only_fields = fields

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

    def get_tracking_code(self, obj):
        if obj.status != OrderStatus.SHIPPED:
            return None

        return obj.tracking_code

    def get_payment_intent(self, obj):
        payment_intent = (
            obj.payment_intents
            .filter(
                status__in=[
                    PaymentIntentStatus.PENDING_PAYMENT,
                    PaymentIntentStatus.RECEIPT_SUBMITTED,
                    PaymentIntentStatus.UNDER_REVIEW,
                    PaymentIntentStatus.MANUAL_REVIEW,
                    PaymentIntentStatus.REJECTED,
                ]
            )
            .order_by("-created_at")
            .first()
        )

        if payment_intent is None:
            return None

        if payment_intent.status in {
            PaymentIntentStatus.PENDING_PAYMENT,
            PaymentIntentStatus.REJECTED,
        }:
            expires_at = payment_intent.expires_at
        else:
            expires_at = None

        return {
            "id": payment_intent.id,
            "token": str(payment_intent.token),
            "status": payment_intent.status,
            "expires_at": expires_at,
            "can_upload_receipt": (
                payment_intent.status in RECEIPT_UPLOAD_STATUSES
            ),
        }
