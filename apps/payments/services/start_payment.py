from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from apps.payments.models import (
    Payment,
    PaymentStatus,
)
from apps.payments.gateways.factory import (
    get_payment_gateway,
)


def start_payment(
        *,
        payment: Payment,
):
    """
    Start payment process through gateway.
    """

    if payment.status != PaymentStatus.PENDING:
        raise ValidationError(
            _("This payment cannot be started.")
        )

    gateway = get_payment_gateway()

    try:
        result = gateway.create_payment(
            payment=payment,
            callback_url=settings.PAYMENT_CALLBACK_URL,
        )

    except Exception:
        raise ValidationError(
            _("Unable to start payment.")
        )

    payment.status = PaymentStatus.PROCESSING

    if result.get(
            "payment_id"
    ):
        payment.gateway_payment_id = (
            result["payment_id"]
        )

    payment.save(
        update_fields=[
            "status",
            "gateway_payment_id",
        ]
    )

    return {
        "payment": payment,
        "redirect_url": result["redirect_url"],
    }
