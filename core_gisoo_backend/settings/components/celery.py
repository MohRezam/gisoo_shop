import os

from decouple import config

from .constants import PROJECT_NAME

CELERY_BROKER_URL = config("CELERY_BROKER_URL", "")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", "")
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_TIME_LIMIT = 800
CELERY_TASK_SOFT_TIME_LIMIT = 740
CELERY_RESULT_EXPIRES = 60 * 20
CELERY_WORKER_PREFETCH_MULTIPLIER = 1

if config("REDIS_MODE", "default") != "default":
    CELERY_BROKER_URL = (
        config("REDIS_URL", "")
        + f"?service_name={config('REDIS_SERVICE_NAME', 'master')}"
    )
    CELERY_BROKER_PASSWORD = config("REDIS_PASSWORD")
    CELERY_RESULT_BACKEND = (
        config("REDIS_URL", "")
        + f"?service_name={config('REDIS_SERVICE_NAME', 'master')}"
    )
    CELERY_RESULT_BACKEND_PASSWORD = config("REDIS_PASSWORD", "")
    CELERY_BROKER_TRANSPORT_OPTIONS = {
        "master_name": "master",
        "sentinel_kwargs": {"password": config("REDIS_PASSWORD", "")},
        "sentinels": [
            (config("REDIS_HOST", ""), config("REDIS_PORT", 26379, cast=int)),
        ],
        "connection_pool_class": "redis.sentinel.SentinelConnectionPool",
        "client_class": "django_redis.client.SentinelClient",
        "parser_class": "redis.connection.HiredisParser",
        # Add more sentinel hosts if you have more.
    }

    CELERY_RESULT_BACKEND_TRANSPORT_OPTIONS = {
        "master_name": "master",
        "sentinel_kwargs": {"password": config("REDIS_PASSWORD", "")},
        "sentinels": [
            (config("REDIS_HOST", ""), config("REDIS_PORT", 26379, cast=int)),
        ],
        "connection_pool_class": "redis.sentinel.SentinelConnectionPool",
        "client_class": "django_redis.client.SentinelClient",
        "parser_class": "redis.connection.HiredisParser",
        # Add more sentinel hosts if you have more.
    }

os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"{PROJECT_NAME}.settings")
