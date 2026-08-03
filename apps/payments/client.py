import requests

from django.conf import settings


class ZarinpalClient:

    def __init__(self):
        if settings.ZARINPAL_SANDBOX:
            self.base_url = (
                "https://sandbox.zarinpal.com/pg/v4/payment"
            )
            self.start_pay_url = (
                "https://sandbox.zarinpal.com/pg/StartPay/"
            )
        else:
            self.base_url = (
                "https://payment.zarinpal.com/pg/v4/payment"
            )
            self.start_pay_url = (
                "https://payment.zarinpal.com/pg/StartPay/"
            )

    def create_payment(
        self,
        *,
        amount: int,
        description: str,
        callback_url: str,
    ):
        response = requests.post(
            f"{self.base_url}/request.json",
            json={
                "merchant_id": settings.ZARINPAL_MERCHANT_ID,
                "amount": amount,
                "description": description,
                "callback_url": callback_url,
            },
            timeout=15,
        )

        response.raise_for_status()

        return response.json()

    def verify_payment(
        self,
        *,
        amount: int,
        authority: str,
    ):
        response = requests.post(
            f"{self.base_url}/verify.json",
            json={
                "merchant_id": settings.ZARINPAL_MERCHANT_ID,
                "amount": amount,
                "authority": authority,
            },
            timeout=15,
        )

        response.raise_for_status()

        return response.json()