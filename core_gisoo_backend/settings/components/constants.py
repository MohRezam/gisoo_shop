from decouple import config

CLIENT_URL = config("CLIENT_URL", default="")
IN_APP_LOG_LEVEL = int(config("LOG_LEVEL", default=3))
PROJECT_NAME = config("APP_BASE_NAME", "core_gisoo_backend")
SIGN_UP_TOKEN_EXPIRE_TIME = config(
    "SIGN_UP_TOKEN_EXPIRE_TIME", default=60 * 60 * 2, cast=int
)
SIGN_UP_TOKEN_PREFIX = "signup_token_"
PHONE_REGEX_PATTERN = "[0-9]+"
# PHONE_REGEX_PATTERN = "^((\([0-9]{3}\))|[0-9]{3})[\s\-]?[\0-9]{3}[\s\-]?[0-9]{4}$" # US numbers
NATIONAL_CODE_REGEX_PATTERN = "^([0-9]{11})$"

LOGGING_STATS_PREFIX = "STATS-"
REQUEST_COUNT_PREFIX = "REQ-COUNT"
RESPONSE_SIZE_PREFIX = "RES-SIZE"
REQUEST_VIEW_NAME_PREFIX = "REQ-VIEW-NAME"
USER_CAPTURE_PREFIX = "USER-ID"
OTP_VALIDATION_REQUEST_PREFIX = "OTP-VALIDATION"
SEND_OTP_REQUEST_PREFIX = "SEND-OTP"
CHANGE_PHONE_PREFIX = "CHANGE-PHONE"

AWS_BOTO_S3_ACCESS_KEY = config("AWS_BOTO_S3_ACCESS_KEY", default="")
AWS_BOTO_S3_SECRET_ACCESS_KEY = config("AWS_BOTO_S3_SECRET_ACCESS_KEY", default="")
AWS_BOTO_S3_DEFAULT_REGION = config("AWS_BOTO_S3_DEFAULT_REGION", default="")

OTP_CHARS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
OTP_LENGTH = int(config("OTP_LENGTH", default=5))
OTP_TTL = int(config("OTP_TTL", default=90))

EBCOM_BASE_URL = config("SHAHKAR_BASE_URL", default="https://sandbox-ebcom.mci.ir")
CAPTCHA_WIDTH = config("CAPTCHA_WIDTH", cast=int, default=200)
CAPTCHA_HEIGHT = config("CAPTCHA_HEIGHT", cast=int, default=100)
CAPTCHA_TYPE = "DIGITS"
ONE_WEEK = 60 * 60 * 24 * 7

SINCH_PROJECT_ID = config("SINCH_PROJECT_ID", default="")
SINCH_ACCESS_KEY_ID = config("SINCH_ACCESS_KEY_ID", default="")
SINCH_SECRET_KEY = config("SINCH_SECRET_KEY", default="")
SINCH_NUMBER = config("SINCH_NUMBER", default="")
SINCH_BODY_MESSAGE = config("SINCH_BODY_MESSAGE", default="")

MANUAL_OTP_METHOD = "manual"
SERVICE_OTP_METHOD = "service"


WISHLIST_COOKIE_NAME = "wishlist_token"
WISHLIST_COOKIE_MAX_AGE = 60 * 60 * 24 * 365