import os

from .common import BASE_DIR, DEBUG
from .constants import PROJECT_NAME

# Static
STATIC_URL = os.getenv("STATIC_URL", "/static/")
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "templates/admin/static")]
if not DEBUG or os.getenv("STAGING", False):
    STATIC_ROOT = "/usr/src/app/static"
    STATICFILES_STORAGE = f"{PROJECT_NAME}.storage_backends.StaticStorage"

# Media

from decouple import config

# Media

if DEBUG:
    MEDIA_URL = config("MEDIA_URL", default="")
    MEDIA_ROOT = os.path.join(BASE_DIR, "")

else:
    STORAGES = {
        "default": {
            "BACKEND": f"{PROJECT_NAME}.storage_backends.MediaStorage",
        },
         "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
    }