from django import template
from django.db.models import Sum
from django.utils import timezone

register = template.Library()


@register.inclusion_tag("admin/gisoo_stats.html", takes_context=True)
def gisoo_dashboard_stats(context):
    """Aggregate shop KPIs for the admin index."""
    today = timezone.localdate()
    stats = {
        "orders_today": 0,
        "orders_total": 0,
        "waiting_payment": 0,
        "payment_review": 0,
        "preparing": 0,
        "shipped": 0,
        "revenue_today": 0,
        "users_total": 0,
        "products_total": 0,
        "unread_inbox": 0,
    }

    try:
        from apps.orders.models import Order, OrderStatus

        stats["orders_total"] = Order.objects.count()
        stats["orders_today"] = Order.objects.filter(created_at__date=today).count()
        stats["waiting_payment"] = Order.objects.filter(
            status__in=[OrderStatus.CREATED, OrderStatus.WAITING_PAYMENT]
        ).count()
        stats["preparing"] = Order.objects.filter(status=OrderStatus.PREPARING).count()
        stats["shipped"] = Order.objects.filter(status=OrderStatus.SHIPPED).count()
        stats["revenue_today"] = (
            Order.objects.filter(
                created_at__date=today,
                status__in=[
                    OrderStatus.PREPARING,
                    OrderStatus.SHIPPED,
                    OrderStatus.DELIVERED,
                ],
            ).aggregate(total=Sum("total_price"))["total"]
            or 0
        )
    except Exception:
        pass

    try:
        from apps.payments.models import PaymentIntent, PaymentIntentStatus

        stats["payment_review"] = PaymentIntent.objects.filter(
            status__in=[
                PaymentIntentStatus.RECEIPT_SUBMITTED,
                PaymentIntentStatus.UNDER_REVIEW,
                PaymentIntentStatus.MANUAL_REVIEW,
            ]
        ).count()
    except Exception:
        pass

    try:
        from apps.users.models import User

        stats["users_total"] = User.objects.count()
    except Exception:
        pass

    try:
        from apps.products.models import Product

        stats["products_total"] = Product.objects.filter(is_available=True).count()
    except Exception:
        pass

    try:
        from apps.notifications.models import InAppNotification

        stats["unread_inbox"] = InAppNotification.objects.filter(is_read=False).count()
    except Exception:
        pass

    return {"stats": stats, "request": context.get("request")}
