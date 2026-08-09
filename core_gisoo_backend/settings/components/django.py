import os

from .common import BASE_DIR, DEBUG
from .constants import PROJECT_NAME

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-development-only-key",
)

ENCRYPTION_KEY = os.getenv(
    "ENCRYPTION_KEY",
    "viyLb459xpvqo3aUVB5WFXnZr1hsUDgVhoRsAa7wEt0=",
).encode()

ALLOWED_HOSTS = ["*"] if DEBUG else [
    os.getenv("ALLOWED_HOSTS"),
]

INTERNAL_IPS = [
    "127.0.0.1",
]

ROOT_URLCONF = f"{PROJECT_NAME}.urls"

WSGI_APPLICATION = f"{PROJECT_NAME}.wsgi.application"

# Proxy / HTTPS
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

if not DEBUG:
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"

    SECURE_HSTS_SECONDS = 86400
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    SECURE_REFERRER_POLICY = "same-origin"

    CSRF_TRUSTED_ORIGINS = [
        "https://donation.darkube.app",
        "https://core-donation.dv.mci.dev",
        "https://core-donation.stzarebin.ir",
        "https://donation.stzarebin.ir",
        "https://donation.pr.mci.dev",
    ]
