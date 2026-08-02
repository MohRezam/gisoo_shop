from decouple import config

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
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "HOST": config("DB_HOST", default="localhost"),
            "PORT": config("DB_PORT", default=""),
            "NAME": config("DB_NAME", default="gisoo-db"),
            "USER": config("DB_USER", default="gisso-user"),
            "PASSWORD": config("DB_PASSWORD", default="gisso-pass:)"),
            "TEST": {
                "NAME": f"test_{PROJECT_NAME}",
            },
        }
    }

CONN_MAX_AGE = 60
