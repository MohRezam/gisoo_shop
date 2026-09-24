from decouple import config


def _as_int(value):
    """Treat missing/blank env values as 0 (decouple cast=int fails on '')."""
    if value is None:
        return 0
    text = str(value).strip()
    if not text:
        return 0
    return int(text)


def _first(*values, default=""):
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return default


SMS_ENABLED = config(
    "SMS_ENABLED",
    default=False,
    cast=bool,
)

SMS_SOAP_URL = config(
    "SMS_SOAP_URL",
    default=(
        "http://api.payamak-panel.com/post/"
        "Send.asmx/SendByBaseNumber"
    ),
)

SMS_CREDIT_URL = config(
    "SMS_CREDIT_URL",
    default=(
        "https://api.payamak-panel.com/post/"
        "Actions.asmx/GetCredit"
    ),
)

# Prefer SMS_USERNAME / SMS_PASSWORD; fall back to legacy sample names.
SMS_USERNAME = _first(
    config("SMS_USERNAME", default=""),
    config("SMS_SERVER_USERNAME", default=""),
)

SMS_PASSWORD = _first(
    config("SMS_PASSWORD", default=""),
    config("SMS_SERVER_PASSWORD", default=""),
    config("MELIPAYAMAK_PASSWORD", default=""),
)

# --- Pattern bodyIds (Melipayamak panel) ---
# Prefer SMS_*_BODY_ID; keep SMS_PATTERN_* aliases for older .env files.

SMS_OTP_BODY_ID = _as_int(
    _first(
        config("SMS_OTP_BODY_ID", default=""),
        config("SMS_PATTERN_OTP", default=""),
        default="0",
    )
)
# Backward-compatible alias used in older docs/tests.
SMS_PATTERN_OTP = SMS_OTP_BODY_ID

SMS_PATTERN_ORDER_CREATED_BODY_ID = _as_int(
    _first(
        config("SMS_PATTERN_ORDER_CREATED_BODY_ID", default=""),
        config("SMS_PATTERN_ORDER_CREATED", default=""),
        default="0",
    )
)
SMS_PATTERN_ORDER_CREATED = SMS_PATTERN_ORDER_CREATED_BODY_ID

SMS_PATTERN_PAYMENT_SUCCESS_BODY_ID = _as_int(
    _first(
        config("SMS_PATTERN_PAYMENT_SUCCESS_BODY_ID", default=""),
        config("SMS_PATTERN_PAYMENT_SUCCESS", default=""),
        default="0",
    )
)
SMS_PATTERN_PAYMENT_SUCCESS = SMS_PATTERN_PAYMENT_SUCCESS_BODY_ID

SMS_PATTERN_PAYMENT_REMINDER_BODY_ID = _as_int(
    _first(
        config("SMS_PATTERN_PAYMENT_REMINDER_BODY_ID", default=""),
        config("SMS_PATTERN_PAYMENT_REMINDER", default=""),
        default="0",
    )
)
SMS_PATTERN_PAYMENT_REMINDER = SMS_PATTERN_PAYMENT_REMINDER_BODY_ID

SMS_PATTERN_NEW_CONSULTATION_BODY_ID = _as_int(
    _first(
        config("SMS_PATTERN_NEW_CONSULTATION_BODY_ID", default=""),
        config("SMS_PATTERN_NEW_CONSULTATION", default=""),
        default="0",
    )
)
SMS_PATTERN_NEW_CONSULTATION = SMS_PATTERN_NEW_CONSULTATION_BODY_ID

SMS_PATTERN_NEW_COMMENT_BODY_ID = _as_int(
    _first(
        config("SMS_PATTERN_NEW_COMMENT_BODY_ID", default=""),
        config("SMS_PATTERN_NEW_COMMENT", default=""),
        default="0",
    )
)
SMS_PATTERN_NEW_COMMENT = SMS_PATTERN_NEW_COMMENT_BODY_ID

SMS_PATTERN_NEW_IMAGE_BODY_ID = _as_int(
    _first(
        config("SMS_PATTERN_NEW_IMAGE_BODY_ID", default=""),
        config("SMS_PATTERN_NEW_IMAGE", default=""),
        default="0",
    )
)
SMS_PATTERN_NEW_IMAGE = SMS_PATTERN_NEW_IMAGE_BODY_ID

SMS_PATTERN_ORDER_SHIPPED_BODY_ID = _as_int(
    _first(
        config("SMS_PATTERN_ORDER_SHIPPED_BODY_ID", default=""),
        config("SMS_PATTERN_ORDER_SHIPPED", default=""),
        default="0",
    )
)
SMS_PATTERN_ORDER_SHIPPED = SMS_PATTERN_ORDER_SHIPPED_BODY_ID

SMS_PATTERN_ORDER_CANCELLED_BODY_ID = _as_int(
    _first(
        config("SMS_PATTERN_ORDER_CANCELLED_BODY_ID", default=""),
        config("SMS_PATTERN_ORDER_CANCELLED", default=""),
        default="0",
    )
)
SMS_PATTERN_ORDER_CANCELLED = SMS_PATTERN_ORDER_CANCELLED_BODY_ID

SMS_PATTERN_DELIVERY_CONFIRM_BODY_ID = _as_int(
    _first(
        config("SMS_PATTERN_DELIVERY_CONFIRM_BODY_ID", default=""),
        config("SMS_PATTERN_DELIVERY_CONFIRM", default=""),
        default="0",
    )
)
SMS_PATTERN_DELIVERY_CONFIRM = SMS_PATTERN_DELIVERY_CONFIRM_BODY_ID

# When Melipayamak is live, OTP pattern text in the panel should be:
#   سلام
#   کد ورود تو: {0}
#   این کد را به کسی ندهید.
#   لغو11
# Set SMS_OTP_BODY_ID to the approved pattern id from the panel.
