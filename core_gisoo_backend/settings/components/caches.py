from decouple import config

if config("REDIS_MODE", "default") == "sentinel":
    DJANGO_REDIS_CONNECTION_FACTORY = "django_redis.pool.SentinelConnectionFactory"

if config("REDIS_MODE", "default") == "gitlab_ci":
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
        }
    }

if config("REDIS_MODE", "default") == "default":
    CACHES = {
        "default": {"BACKEND": "apps.shared.cache.base_cache.FallbackCache"},
        "redis": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": config("REDIS_URL", ""),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "PARSER_CLASS": "redis.connection.DefaultParser",
                "PASSWORD": config("REDIS_PASSWORD", ""),  # Add the password here
            },
            "KEY_PREFIX": config("CACHE_PREFIX", ""),
        },
        "database": {
            "BACKEND": "django.core.cache.backends.db.DatabaseCache",
            "LOCATION": "cache_table",
            "KEY_FUNCTION": "apps.shared.cache.utils.make_key",
        },
    }

if config("REDIS_MODE", "default") == "sentinel":
    CACHES = {
        "default": {"BACKEND": "apps.shared.cache.base_cache.FallbackCache"},
        "redis": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": config("REDIS_URL", "")
            + f"?service_name={config('REDIS_SERVICE_NAME', 'master')}",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.SentinelClient",
                "PARSER_CLASS": "redis.connection.HiredisParser",
                "SENTINELS": [
                    (config("REDIS_HOST", ""), config("REDIS_PORT", 26379, cast=int))
                ],
                "SENTINEL_KWARGS": {"password": config("REDIS_PASSWORD", "")},
                "CONNECTION_POOL_CLASS": "redis.sentinel.SentinelConnectionPool",
            },
            "KEY_PREFIX": config("CACHE_PREFIX", ""),
        },
        "database": {
            "BACKEND": "django.core.cache.backends.db.DatabaseCache",
            "LOCATION": "cache_table",
            "KEY_FUNCTION": "apps.shared.cache.utils.make_key",
        },
    }
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

CACHE_TTL = 60 * 15
FAVORITE_CACHE_TTL = 60 * 60 * 24 * 2  # 2 days
