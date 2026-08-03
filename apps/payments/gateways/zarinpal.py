from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from apps.payments.client import (
    ZarinpalClient,
)
from apps.payments.gateways.base import (
    BasePaymentGateway,
)


class ZarinpalGateway(
    BasePaymentGateway,
):

    def __init__(self):
        self.client = ZarinpalClient()

    def create_payment(
            self,
            *,
            payment,
            callback_url: str,
    ):
        response = self.client.create_payment(
            amount=payment.amount,
            description=f"Order #{payment.order.id}",
            callback_url=callback_url,
        )

        data = response.get(
            "data",
            {},
        )

        if data.get("code") != 100:
            raise ValidationError(
                _("Unable to create payment.")
            )

        authority = data["authority"]

        return {
            "payment_id": authority,
            "redirect_url": (
                f"{self.client.start_pay_url}{authority}"
            ),
        }

    def verify_payment(
            self,
            *,
            payment,
            authority: str,
    ):
        response = self.client.verify_payment(
            amount=payment.amount,
            authority=authority,
        )

        data = response.get(
            "data",
            {},
        )

        if data.get("code") not in [
            100,
            101,
        ]:
            return {
                "success": False,
                "reference_id": "",
            }

        return {
            "success": True,
            "reference_id": str(
                data["ref_id"]
            ),
        }
