from django.conf import settings

from apps.payments.gateways.zarinpal import (
    ZarinpalGateway,
)


def get_payment_gateway():
    gateway = settings.PAYMENT_GATEWAY

    gateways = {
        "zarinpal": ZarinpalGateway,
    }

    gateway_class = gateways.get(
        gateway,
    )

    if gateway_class is None:
        raise ValueError(
            f"Unsupported payment gateway: {gateway}"
        )

    return gateway_class()