import os

from django.conf import settings

from .common import BASE_DIR, DEBUG
from .constants import PROJECT_NAME

SECRET_KEY = os.getenv(
    "SECRET_KEY", "django-insecure-*6^r370f68i&-l*g2b*ncvy*57wv6!da5$6o8glho@)&z@ruf="
)
ENCRYPTION_KEY = os.getenv(
    "ENCRYPTION_KEY", b"viyLb459xpvqo3aUVB5WFXnZr1hsUDgVhoRsAa7wEt0="
)

ALLOWED_HOSTS = ["*"]

if DEBUG:
    ALLOWED_HOSTS += ["127.0.0.1", "localhost", "*"]

INTERNAL_IPS = ["127.0.0.1"]

ROOT_URLCONF = f"{PROJECT_NAME}.urls"

# MEDIA_URL = "/medias/"
# MEDIA_ROOT = os.path.join(BASE_DIR, "medias")


WSGI_APPLICATION = f"{PROJECT_NAME}.wsgi.application"


# Configure HTTPS
USE_X_FORWARDED_HOST = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

if not settings.DEBUG:
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_HSTS_SECONDS = 86400
    SECURE_REDIRECT_EXEMPT = []
    SECURE_REFERRER_POLICY = "same-origin"
    CSRF_TRUSTED_ORIGINS = [
        "http://localhost:8000",
        "http://localhost:3000",
        "https://donation.darkube.app",
        "https://core-donation.dv.mci.dev",
        "https://core-donation.stzarebin.ir",
        "https://donation.stzarebin.ir",
        "https://donation.pr.mci.dev",
    ]
