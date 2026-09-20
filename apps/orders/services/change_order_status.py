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


@transaction.atomic
def change_order_status(
    *,
    order: Order,
    new_status: str,
    changed_by=None,
    reason: str = "",
):
    order = (
        Order.objects
        .select_for_update()
        .get(
            pk=order.pk,
        )
    )

    current_status = order.status

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

    if new_status == OrderStatus.SHIPPED:
        from apps.notifications.services.inbox import notify_user
        from apps.orders.cache import invalidate_track_order_cache

        tracking = order.tracking_code or ""
        body = f"سفارش {order.public_number or order.id} ارسال شد."
        if tracking:
            body = f"{body} کد رهگیری: {tracking}"
        notify_user(
            user=order.user,
            title="مرسوله ارسال شد",
            body=body,
            type="order",
            link=f"/account/orders/{order.id}",
            order_id=order.id,
        )
        invalidate_track_order_cache(order.public_number, order.phone_number)

    elif new_status in (
        OrderStatus.PREPARING,
        OrderStatus.DELIVERED,
        OrderStatus.CANCELED,
        OrderStatus.EXPIRED,
        OrderStatus.PAYMENT_REJECTED,
        OrderStatus.WAITING_PAYMENT,
    ):
        from apps.orders.cache import invalidate_track_order_cache

        invalidate_track_order_cache(order.public_number, order.phone_number)

    return order
