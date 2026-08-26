from decouple import config

from .common import DEBUG

REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "utils.exceptions.exception_handler.custom_exception_handler",
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_THROTTLE_CLASSES": [],
    "DEFAULT_THROTTLE_RATES": {
        "anon": config("THROTTLE_RATE_ANON", default="100/minute"),
        "user": config("THROTTLE_RATE_USER", default="1000/day"),
        "otp": config("THROTTLE_RATE_OTP", default="2/minute"),
        "consultation_create": "8/day",
        "guest_otp_request": "10/hour",
        "guest_otp_verify": "10/hour",
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
if not DEBUG:
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (
        "rest_framework.renderers.JSONRenderer",
    )
