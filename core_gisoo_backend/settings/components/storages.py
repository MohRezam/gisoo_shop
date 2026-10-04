import os

from decouple import config

from .common import BASE_DIR, DEBUG
from .constants import PROJECT_NAME

# Static
STATIC_URL = os.getenv("STATIC_URL", "/static/")
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "templates/admin/static")]

# false/0/empty (and unset) => False; only true/1/yes enable staging.
STAGING = str(os.getenv("STAGING", "")).lower() in ("true", "1", "yes")

if not DEBUG or STAGING:
    # Align with Dockerfile WORKDIR=/app and compose/nginx volume mounts.
    STATIC_ROOT = "/app/static"
    STATICFILES_STORAGE = f"{PROJECT_NAME}.storage_backends.StaticStorage"

# Media

if DEBUG:
    MEDIA_URL = config("MEDIA_URL", default="/media/")
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")

else:
    STORAGES = {
        "default": {
            "BACKEND": f"{PROJECT_NAME}.storage_backends.MediaStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
