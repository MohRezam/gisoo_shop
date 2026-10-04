from apps.orders.constants import ORDER_STATUS_LABELS
from apps.orders.models import Order, OrderStatus


TRACK_STEPS = [
    ("created", "ثبت سفارش"),
    ("waiting_payment", "در انتظار پرداخت"),
    ("paid", "پرداخت تأیید شد"),
    ("preparing", "آماده‌سازی"),
    ("shipped", "ارسال"),
    ("delivered", "تحویل"),
]


def build_track_payload(order: Order) -> dict:
    status = order.status
    status_label = ORDER_STATUS_LABELS.get(status, status)

    paid = status in (
        OrderStatus.PREPARING,
        OrderStatus.SHIPPED,
        OrderStatus.DELIVERED,
    ) or order.payment_intents.filter(status="paid").exists()

    timestamps = {
        "created": order.created_at,
        "waiting_payment": order.created_at,
        "paid": order.prepared_at if paid else None,
        "preparing": order.prepared_at,
        "shipped": order.shipped_at,
        "delivered": order.delivered_at,
    }

    done_map = {
        "created": True,
        "waiting_payment": status
        not in (OrderStatus.CANCELED, OrderStatus.EXPIRED)
        or status == OrderStatus.WAITING_PAYMENT
        or status == OrderStatus.PAYMENT_REJECTED
        or paid,
        "paid": paid,
        "preparing": status
        in (OrderStatus.PREPARING, OrderStatus.SHIPPED, OrderStatus.DELIVERED),
        "shipped": status in (OrderStatus.SHIPPED, OrderStatus.DELIVERED),
        "delivered": status == OrderStatus.DELIVERED,
    }

    if status == OrderStatus.PAYMENT_REJECTED:
        done_map["waiting_payment"] = True
        done_map["paid"] = False

    steps = [
        {
            "key": key,
            "label": label,
            "done": bool(done_map.get(key)),
            "at": timestamps.get(key),
        }
        for key, label in TRACK_STEPS
    ]

    items = list(order.items.all()[:5])
    if items:
        titles = [item.product_title for item in items]
        items_summary = "، ".join(titles)
        extra = order.items.count() - len(items)
        if extra > 0:
            items_summary = f"{items_summary} و {extra} مورد دیگر"
    else:
        items_summary = None

    tracking_code = None
    if status not in (OrderStatus.CANCELED, OrderStatus.EXPIRED):
        tracking_code = order.tracking_code or None
        shipment = order.shipments.order_by("-created_at").first()
        if shipment and shipment.tracking_code:
            tracking_code = shipment.tracking_code

    return {
        "public_number": order.public_number,
        "status": status,
        "status_label": status_label,
        "tracking_code": tracking_code,
        "steps": steps,
        "items_summary": items_summary,
    }
