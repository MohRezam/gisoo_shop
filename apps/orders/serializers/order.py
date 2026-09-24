from rest_framework import serializers

from apps.orders.models import (
    Order,
    OrderBundle,
    OrderItem,
    OrderStatus,
)
from apps.orders.services.delivery_confirm import (
    customer_can_confirm_delivery,
    get_estimate_bounds,
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
    tracking_code = serializers.SerializerMethodField()
    carrier = serializers.SerializerMethodField()
    tracking_url = serializers.SerializerMethodField()
    shipped_at = serializers.DateTimeField(read_only=True)
    estimated_days_min = serializers.SerializerMethodField()
    estimated_days = serializers.SerializerMethodField()
    can_confirm_delivery = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "public_number",
            "order_name",
            "status",
            "total_price",
            "created_at",
            "expires_at",
            "items_count",
            "items",
            "bundles",
            "payment_intent",
            "tracking_code",
            "carrier",
            "tracking_url",
            "shipped_at",
            "estimated_days_min",
            "estimated_days",
            "can_confirm_delivery",
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

    def get_tracking_code(self, obj):
        return OrderDetailSerializer.get_tracking_code(self, obj)

    def get_carrier(self, obj):
        return OrderDetailSerializer.get_carrier(self, obj)

    def get_tracking_url(self, obj):
        return OrderDetailSerializer.get_tracking_url(self, obj)

    def get_estimated_days_min(self, obj):
        return OrderDetailSerializer.get_estimated_days_min(self, obj)

    def get_estimated_days(self, obj):
        return OrderDetailSerializer.get_estimated_days(self, obj)

    def get_can_confirm_delivery(self, obj):
        return OrderDetailSerializer.get_can_confirm_delivery(self, obj)


class OrderDetailSerializer(serializers.ModelSerializer):
    items_count = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    bundles = serializers.SerializerMethodField()
    tracking_code = serializers.SerializerMethodField()
    carrier = serializers.SerializerMethodField()
    tracking_url = serializers.SerializerMethodField()
    payment_intent = serializers.SerializerMethodField()
    shipped_at = serializers.DateTimeField(read_only=True)
    estimated_days_min = serializers.SerializerMethodField()
    estimated_days = serializers.SerializerMethodField()
    can_confirm_delivery = serializers.SerializerMethodField()

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
            "carrier",
            "tracking_url",
            "payment_intent",
            "phone_number",
            "province",
            "city",
            "address",
            "expires_at",
            "shipped_at",
            "estimated_days_min",
            "estimated_days",
            "can_confirm_delivery",
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

    def get_estimated_days_min(self, obj):
        min_days, _ = get_estimate_bounds(obj)
        return min_days

    def get_estimated_days(self, obj):
        _, max_days = get_estimate_bounds(obj)
        return max_days

    def get_can_confirm_delivery(self, obj):
        return customer_can_confirm_delivery(obj)

    def get_tracking_code(self, obj):
        if obj.status in (
            OrderStatus.CANCELED,
            OrderStatus.EXPIRED,
        ):
            return None
        if obj.status not in (
            OrderStatus.SHIPPED,
            OrderStatus.DELIVERED,
        ):
            return None
        code = (obj.tracking_code or "").strip()
        return code or None

    def get_carrier(self, obj):
        carrier = (obj.carrier or "").strip()
        if carrier:
            return carrier
        method = getattr(obj, "shipping_method", None)
        if method and method.carrier:
            return method.carrier
        return None

    def get_tracking_url(self, obj):
        if obj.status in (
            OrderStatus.CANCELED,
            OrderStatus.EXPIRED,
        ):
            return None
        if obj.status not in (
            OrderStatus.SHIPPED,
            OrderStatus.DELIVERED,
        ):
            return None
        from apps.shipping.models import (
            CARRIER_TRACKING_URLS,
            ShippingCarrier,
        )

        carrier = self.get_carrier(obj)
        if not carrier:
            return None
        return CARRIER_TRACKING_URLS.get(
            carrier,
            CARRIER_TRACKING_URLS[ShippingCarrier.POST],
        )

    def get_payment_intent(self, obj):
        if obj.status in (
            OrderStatus.EXPIRED,
            OrderStatus.CANCELED,
            OrderStatus.PREPARING,
            OrderStatus.SHIPPED,
            OrderStatus.DELIVERED,
        ):
            return None

        from django.utils import timezone

        payment_intent = (
            obj.payment_intents
            .filter(
                status__in=[
                    PaymentIntentStatus.PENDING_PAYMENT,
                    PaymentIntentStatus.RECEIPT_SUBMITTED,
                    PaymentIntentStatus.REJECTED,
                ]
            )
            .order_by("-created_at")
            .first()
        )

        if payment_intent is None:
            return None

        # Under review: keep intent visible even after the original deadline.
        if payment_intent.status == PaymentIntentStatus.RECEIPT_SUBMITTED:
            return {
                "id": payment_intent.id,
                "token": str(payment_intent.token),
                "status": payment_intent.status,
                "expires_at": None,
                "can_upload_receipt": False,
                "rejection_reason": "",
            }

        now = timezone.now()
        order_deadline_passed = (
            obj.expires_at is not None and obj.expires_at <= now
        )
        intent_deadline_passed = (
            payment_intent.expires_at is not None
            and payment_intent.expires_at <= now
        )
        if order_deadline_passed or intent_deadline_passed:
            # Payment window closed — do not offer resume / cancel via intent.
            return None

        return {
            "id": payment_intent.id,
            "token": str(payment_intent.token),
            "status": payment_intent.status,
            "expires_at": payment_intent.expires_at,
            "can_upload_receipt": (
                payment_intent.status in RECEIPT_UPLOAD_STATUSES
            ),
            "rejection_reason": (
                payment_intent.rejection_reason or ""
                if payment_intent.status == PaymentIntentStatus.REJECTED
                else ""
            ),
        }
