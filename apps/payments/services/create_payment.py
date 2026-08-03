from apps.payments.models import (
    Payment,
    PaymentStatus,
)


def create_payment(
        *,
        order,
):
    return Payment.objects.create(
        order=order,
        amount=order.total_price,
        status=PaymentStatus.PENDING,
    )
