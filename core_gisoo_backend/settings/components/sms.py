from decouple import config


SMS_PATTERN_OTP = config(
    "SMS_PATTERN_OTP",
    cast=int,
)

SMS_PATTERN_ORDER_CREATED = config(
    "SMS_PATTERN_ORDER_CREATED",
    cast=int,
)

SMS_PATTERN_PAYMENT_SUCCESS = config(
    "SMS_PATTERN_PAYMENT_SUCCESS",
    cast=int,
)

SMS_PATTERN_NEW_CONSULTATION = config(
    "SMS_PATTERN_NEW_CONSULTATION",
    cast=int,
)

SMS_PATTERN_NEW_COMMENT = config(
    "SMS_PATTERN_NEW_COMMENT",
    cast=int,
)

SMS_PATTERN_NEW_IMAGE = config(
    "SMS_PATTERN_NEW_IMAGE",
    cast=int,
)

SMS_PATTERN_ORDER_SHIPPED = config(
    "SMS_PATTERN_ORDER_SHIPPED",
    cast=int,
)

SMS_PATTERN_ORDER_CANCELLED = config(
    "SMS_PATTERN_ORDER_CANCELLED",
    cast=int,
)