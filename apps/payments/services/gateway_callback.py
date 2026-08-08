from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from apps.payments.models import (
    Payment,
)
from apps.payments.services.verify_payment import (
    verify_payment,
)


def gateway_callback(
    *,
    authority: str,
):
    """
    Handle payment gateway callback.
    """

    if not authority:
        raise ValidationError(
            _("Invalid payment authority.")
        )

    payment = (
        Payment.objects
        .select_related(
            "order",
        )
        .filter(
            gateway_payment_id=authority,
        )
        .first()
    )

    if payment is None:
        raise ValidationError(
            _("Payment not found.")
        )

    verify_payment(
        payment=payment,
        authority=authority,
    )

    return payment