"""
Legacy gateway payment creation.

The Payment / PaymentStatus models were removed in favor of
card-to-card PaymentIntent flow. This stub remains so imports
do not crash; it must not be used by live URLs.
"""


def create_payment(*, order):
    raise NotImplementedError(
        "Legacy gateway Payment is no longer supported. "
        "Use PaymentIntent instead."
    )
