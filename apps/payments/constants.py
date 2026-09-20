from decouple import config

# Monetary amounts in PaymentIntent / Order pricing are stored and returned in تومان (IRT).
PAYMENT_AMOUNT_UNIT = "toman"
PAYMENT_AMOUNT_UNIT_LABEL = "تومان"

PAYMENT_INTENT_EXPIRATION_MINUTES = int(
    config("PAYMENT_INTENT_EXPIRATION_MINUTES", default=60 * 24)
)

# Fallback destination card when no active PaymentDestinationCard row exists.
DEFAULT_DESTINATION_CARD_NUMBER = config(
    "PAYMENT_DESTINATION_CARD_NUMBER",
    default="6037990000000000",
)
DEFAULT_DESTINATION_BANK_NAME = config(
    "PAYMENT_DESTINATION_BANK_NAME",
    default="بانک ملی",
)
DEFAULT_DESTINATION_HOLDER_NAME = config(
    "PAYMENT_DESTINATION_HOLDER_NAME",
    default="گیسو سنتر",
)
PAYMENT_DESTINATION_CARD_ID = config(
    "PAYMENT_DESTINATION_CARD_ID",
    default=None,
)
