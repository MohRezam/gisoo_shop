from django.db.models import Case, IntegerField, QuerySet, Value, When

from apps.orders.models import OrderStatus

# Lower number = higher priority in lists (preparing first).
STATUS_LIST_PRIORITY = {
    OrderStatus.PREPARING: 0,
    OrderStatus.WAITING_PAYMENT: 1,
    OrderStatus.CREATED: 2,
    OrderStatus.PAYMENT_REJECTED: 3,
    OrderStatus.SHIPPED: 4,
    OrderStatus.DELIVERED: 5,
    OrderStatus.CANCELED: 6,
    OrderStatus.EXPIRED: 7,
}


def apply_status_priority_ordering(queryset: QuerySet) -> QuerySet:
    """Order by operational priority, then newest first within each status."""
    whens = [
        When(status=status, then=Value(priority))
        for status, priority in STATUS_LIST_PRIORITY.items()
    ]
    return queryset.annotate(
        status_priority=Case(
            *whens,
            default=Value(99),
            output_field=IntegerField(),
        )
    ).order_by("status_priority", "-created_at")
