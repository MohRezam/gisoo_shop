from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from apps.orders.models import (
    OrderStatus,
)
from apps.orders.services.change_order_status import (
    change_order_status,
)
from apps.payments.gateways.factory import (
    get_payment_gateway,
)
from apps.payments.models import (
    Payment,
    PaymentStatus,
)
from django.db import transaction


@transaction.atomic
def verify_payment(
        *,
        payment: Payment,
        authority: str,
):
    payment = (
        Payment.objects
        .select_for_update()
        .select_related("order")
        .get(pk=payment.pk)
    )

    if payment.status == PaymentStatus.SUCCESS:
        return payment

    if payment.status != PaymentStatus.PROCESSING:
        raise ValidationError(
            _("Payment is not ready for verification.")
        )

    gateway = get_payment_gateway()

    result = gateway.verify_payment(
        payment=payment,
        authority=authority,
    )

    if not result["success"]:
        payment.status = PaymentStatus.FAILED

        payment.save(
            update_fields=[
                "status",
            ]
        )

        return payment

    payment.status = PaymentStatus.SUCCESS
    payment.gateway_reference_id = (
        result["reference_id"]
    )
    payment.paid_at = timezone.now()

    payment.save(
        update_fields=[
            "status",
            "gateway_reference_id",
            "paid_at",
        ]
    )

    change_order_status(
        order=payment.order,
        new_status=OrderStatus.PREPARING,
        reason="Payment verified successfully.",
    )

    return payment
