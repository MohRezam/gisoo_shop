from django.core.exceptions import ImproperlyConfigured
from decouple import config

from core_gisoo_backend.settings.components.common import DEBUG
from core_gisoo_backend.settings.components.constants import PROJECT_NAME

local_db_enabled = config("LOCAL_DB_ENABLED", default=False, cast=bool)
if local_db_enabled:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "db.sqlite3",
        }
    }
else:
    db_password = config("DB_PASSWORD", default="")
    if not db_password:
        if DEBUG:
            # Local-dev only; never used when DEBUG is False.
            db_password = "gisso-pass:)"
        else:
            raise ImproperlyConfigured(
                "The DB_PASSWORD environment variable must be set when DEBUG is False."
            )

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "HOST": config("DB_HOST", default="localhost"),
            "PORT": config("DB_PORT", default=""),
            "NAME": config("DB_NAME", default="gisoo-db"),
            "USER": config("DB_USER", default="gisso-user"),
            "PASSWORD": db_password,
            "TEST": {
                "NAME": f"test_{PROJECT_NAME}",
            },
        }
    }

CONN_MAX_AGE = 60
