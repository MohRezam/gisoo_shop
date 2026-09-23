from decouple import config


def _as_int(value):
    """Treat missing/blank env values as 0 (decouple cast=int fails on '')."""
    if value is None:
        return 0
    text = str(value).strip()
    if not text:
        return 0
    return int(text)


SMS_ENABLED = config(
    "SMS_ENABLED",
    default=False,
    cast=bool,
)

SMS_PATTERN_OTP = config(
    "SMS_PATTERN_OTP",
    default=0,
    cast=_as_int,
)

SMS_PATTERN_ORDER_CREATED = config(
    "SMS_PATTERN_ORDER_CREATED",
    default=0,
    cast=_as_int,
)

SMS_PATTERN_PAYMENT_SUCCESS = config(
    "SMS_PATTERN_PAYMENT_SUCCESS",
    default=0,
    cast=_as_int,
)

SMS_PATTERN_PAYMENT_REMINDER = config(
    "SMS_PATTERN_PAYMENT_REMINDER",
    default=0,
    cast=_as_int,
)

SMS_PATTERN_NEW_CONSULTATION = config(
    "SMS_PATTERN_NEW_CONSULTATION",
    default=0,
    cast=_as_int,
)

SMS_PATTERN_NEW_COMMENT = config(
    "SMS_PATTERN_NEW_COMMENT",
    default=0,
    cast=_as_int,
)

SMS_PATTERN_NEW_IMAGE = config(
    "SMS_PATTERN_NEW_IMAGE",
    default=0,
    cast=_as_int,
)

SMS_PATTERN_ORDER_SHIPPED = config(
    "SMS_PATTERN_ORDER_SHIPPED",
    default=0,
    cast=_as_int,
)

SMS_PATTERN_ORDER_CANCELLED = config(
    "SMS_PATTERN_ORDER_CANCELLED",
    default=0,
    cast=_as_int,
)

SMS_PATTERN_DELIVERY_CONFIRM = config(
    "SMS_PATTERN_DELIVERY_CONFIRM",
    default=0,
    cast=_as_int,
)

# When Melipayamak is live, OTP SMS body/pattern should include the domain
# so mobile autofill works, e.g.:
#   کد ورود: @gisoo.example #123456
# Pattern args for OTP remain: [otp] (and optionally domain as second arg).
# Delivery confirm pattern args: [order_id] — text should ask the customer
# to open the site and tap «تحویل گرفتم».
