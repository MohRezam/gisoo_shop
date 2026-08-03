from apps.orders.models import OrderStatus


ORDER_EXPIRATION_MINUTES = 15

MAX_ORDER_DESCRIPTION_LENGTH = 500

MAX_PAYMENT_RETRY = 3


ALLOWED_TRANSITIONS = {
    OrderStatus.CREATED: [
        OrderStatus.PREPARING,
        OrderStatus.CANCELED,
        OrderStatus.EXPIRED,
    ],

    OrderStatus.PREPARING: [
        OrderStatus.SHIPPED,
        OrderStatus.CANCELED,
    ],

    OrderStatus.SHIPPED: [
        OrderStatus.DELIVERED,
    ],

    OrderStatus.DELIVERED: [],

    OrderStatus.CANCELED: [],

    OrderStatus.EXPIRED: [],
}