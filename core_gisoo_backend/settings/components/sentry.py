from decouple import config
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=config("SENTRY_URL", ""),
    integrations=[DjangoIntegration()],
    # Keep sampling low by default; override via SENTRY_TRACES_SAMPLE_RATE.
    traces_sample_rate=float(config("SENTRY_TRACES_SAMPLE_RATE", default=0.1)),
    # Do not send PII by default; set SENTRY_SEND_DEFAULT_PII=true to opt in.
    send_default_pii=str(config("SENTRY_SEND_DEFAULT_PII", default="false")).lower()
    in ("true", "1", "yes"),
)
