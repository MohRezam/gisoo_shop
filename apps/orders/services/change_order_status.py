from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from apps.orders.constants import ALLOWED_TRANSITIONS
from apps.orders.models import (
    Order,
    OrderStatus,
    OrderStatusHistory,
)


STATUS_NOTIFICATIONS = {
    OrderStatus.PREPARING: (
        "سفارش در حال آماده‌سازی است",
        "سفارش {label} تأیید شد و در حال آماده‌سازی است.",
    ),
    OrderStatus.SHIPPED: (
        "مرسوله ارسال شد",
        "سفارش {label} ارسال شد.",
    ),
    OrderStatus.DELIVERED: (
        "سفارش تحویل شد",
        "سفارش {label} با موفقیت تحویل داده شد.",
    ),
    OrderStatus.CANCELED: (
        "سفارش لغو شد",
        "سفارش {label} لغو شد.",
    ),
    OrderStatus.EXPIRED: (
        "سفارش منقضی شد",
        "مهلت پرداخت سفارش {label} به پایان رسید.",
    ),
    OrderStatus.PAYMENT_REJECTED: (
        "رسید پرداخت رد شد",
        "رسید پرداخت سفارش {label} رد شد. می‌توانید دوباره پرداخت را ارسال کنید.",
    ),
    OrderStatus.WAITING_PAYMENT: (
        "در انتظار پرداخت",
        "سفارش {label} در انتظار پرداخت است.",
    ),
}


@transaction.atomic
def change_order_status(
    *,
    order: Order,
    new_status: str,
    changed_by=None,
    reason: str = "",
    send_notification: bool = True,
):
    order = (
        Order.objects
        .select_for_update()
        .select_related("user")
        .get(
            pk=order.pk,
        )
    )

    current_status = order.status

    # اگر وضعیت تغییری نکرده، کاری انجام نده
    if current_status == new_status:
        return order

    allowed = ALLOWED_TRANSITIONS.get(
        current_status,
        [],
    )

    if new_status not in allowed:
        raise ValidationError(
            _("Invalid order status transition.")
        )

    update_fields = [
        "status",
    ]

    order.status = new_status

    now = timezone.now()

    if (
        new_status == OrderStatus.PREPARING and
        order.prepared_at is None
    ):
        order.prepared_at = now
        update_fields.append(
            "prepared_at",
        )

    elif (
        new_status == OrderStatus.SHIPPED and
        order.shipped_at is None
    ):
        order.shipped_at = now
        update_fields.append(
            "shipped_at",
        )

    elif (
        new_status == OrderStatus.DELIVERED and
        order.delivered_at is None
    ):
        order.delivered_at = now
        update_fields.append(
            "delivered_at",
        )

    order.save(
        update_fields=update_fields,
    )

    OrderStatusHistory.objects.create(
        order=order,
        old_status=current_status,
        new_status=new_status,
        changed_by=changed_by,
        reason=reason,
    )

    if send_notification and new_status in STATUS_NOTIFICATIONS:
        from apps.notifications.services.inbox import notify_user
        from apps.orders.cache import invalidate_track_order_cache

        title, body_template = STATUS_NOTIFICATIONS[new_status]
        label = order.public_number or order.id
        body = body_template.format(label=label)

        if new_status == OrderStatus.SHIPPED and order.tracking_code:
            body = f"{body} کد رهگیری: {order.tracking_code}"

        user = order.user
        order_id = order.id

        transaction.on_commit(
            lambda: notify_user(
                user=user,
                title=title,
                body=body,
                type="order",
                link=f"/account/orders/{order_id}",
                order_id=order_id,
            )
        )

        try:
            invalidate_track_order_cache(
                order.public_number,
                order.phone_number,
            )
        except Exception:
            pass

    return order
