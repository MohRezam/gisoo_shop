from django import template
from django.db.models import Sum
from django.utils import timezone

register = template.Library()


def _pct(part, total):
    if not total:
        return 0
    return round((part / total) * 100)


@register.inclusion_tag("admin/gisoo_stats.html", takes_context=True)
def gisoo_dashboard_stats(context):
    """Aggregate shop KPIs and chart series for the admin index."""
    today = timezone.localdate()
    stats = {
        "orders_today": 0,
        "orders_total": 0,
        "waiting_payment": 0,
        "payment_review": 0,
        "preparing": 0,
        "shipped": 0,
        "delivered": 0,
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
        stats["delivered"] = Order.objects.filter(status=OrderStatus.DELIVERED).count()
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

    status_rows = [
        ("در انتظار پرداخت", stats["waiting_payment"], "#f59e0b"),
        ("آماده‌سازی", stats["preparing"], "#173ded"),
        ("ارسال‌شده", stats["shipped"], "#0ea5e9"),
        ("تحویل‌شده", stats["delivered"], "#10b981"),
        ("رسید در بررسی", stats["payment_review"], "#ef4444"),
    ]
    status_total = sum(v for _, v, _ in status_rows) or 1
    status_chart = [
        {
            "label": label,
            "value": value,
            "color": color,
            "pct": _pct(value, status_total),
        }
        for label, value, color in status_rows
    ]

    bar_rows = [
        ("سفارش امروز", stats["orders_today"], "#173ded"),
        ("کل سفارش", stats["orders_total"], "#0f2fb8"),
        ("کاربران", stats["users_total"], "#6366f1"),
        ("محصول فعال", stats["products_total"], "#8b5cf6"),
        ("اعلان نخوانده", stats["unread_inbox"], "#f43f5e"),
    ]
    bar_max = max((v for _, v, _ in bar_rows), default=1) or 1
    bar_chart = [
        {
            "label": label,
            "value": value,
            "color": color,
            "pct": max(_pct(value, bar_max), 4 if value else 0),
        }
        for label, value, color in bar_rows
    ]

    # Conic-gradient stops for donut (RTL-friendly visual)
    cursor = 0
    gradient_parts = []
    for row in status_chart:
        start = cursor
        cursor += row["pct"]
        gradient_parts.append(f"{row['color']} {start}% {cursor}%")
    donut_gradient = (
        ", ".join(gradient_parts)
        if any(r["value"] for r in status_chart)
        else "#e5e7eb 0% 100%"
    )

    return {
        "stats": stats,
        "status_chart": status_chart,
        "bar_chart": bar_chart,
        "donut_gradient": donut_gradient,
        "status_total": sum(r["value"] for r in status_chart),
        "request": context.get("request"),
    }
