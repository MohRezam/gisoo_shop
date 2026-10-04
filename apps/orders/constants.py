from apps.orders.models import OrderStatus


ORDER_EXPIRATION_MINUTES = 15

MAX_ORDER_DESCRIPTION_LENGTH = 500

MAX_PAYMENT_RETRY = 3


ORDER_STATUS_LABELS = {
    OrderStatus.WAITING_PAYMENT: "در انتظار پرداخت",
    OrderStatus.PAYMENT_REJECTED: "پرداخت رد شده",
    OrderStatus.PREPARING: "در حال آماده‌سازی",
    OrderStatus.SHIPPED: "ارسال شده",
    OrderStatus.DELIVERED: "تحویل شده",
    OrderStatus.CANCELED: "لغو شده",
    OrderStatus.EXPIRED: "منقضی شده",
}


ALLOWED_TRANSITIONS = {
    OrderStatus.WAITING_PAYMENT: [
        OrderStatus.PREPARING,
        OrderStatus.PAYMENT_REJECTED,
        OrderStatus.CANCELED,
        OrderStatus.EXPIRED,
    ],
    OrderStatus.PAYMENT_REJECTED: [
        OrderStatus.WAITING_PAYMENT,
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
