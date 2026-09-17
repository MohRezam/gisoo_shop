from rest_framework import serializers

from apps.orders.models import Order, OrderStatus
from apps.payments.models import PaymentIntentStatus


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


class OrderDetailSerializer(serializers.ModelSerializer):
    items_count = serializers.SerializerMethodField()
    tracking_code = serializers.SerializerMethodField()
    payment_intent = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "created_at",
            "total_price",
            "discount_amount",
            "items_count",
            "tracking_code",
            "payment_intent",
        ]

    def get_items_count(self, obj):
        return sum(
            item.quantity
            for item in obj.items.all()
        )

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

        return {
            "id": payment_intent.id,
            "token": payment_intent.token,
            "status": payment_intent.status,
            "expires_at": payment_intent.expires_at,
            "can_upload_receipt": (
                payment_intent.status
                in {
                    PaymentIntentStatus.PENDING_PAYMENT,
                    PaymentIntentStatus.REJECTED,
                }
            ),
        }


class OrderListSerializer(serializers.ModelSerializer):
    order_name = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "order_name",
            "items_count",
            "status",
            "created_at",
        ]

    def get_order_name(self, obj):
        return f"سفارش #{obj.id}"

    def get_items_count(self, obj):
        return sum(
            item.quantity
            for item in obj.items.all()
        )