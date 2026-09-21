import logging
import socket

from django.core.cache.backends.base import BaseCache

from apps.shared.models.db_cache import CacheTable
from apps.shared.utils import get_cache
from utils.general.logger import Logger

logging.basicConfig()
logger = logging.getLogger("custom")

try:
    from redis.exceptions import ConnectionError as RedisConnectionError
    from redis.exceptions import TimeoutError as RedisTimeoutError
except ImportError:  # pragma: no cover
    RedisConnectionError = ConnectionError
    RedisTimeoutError = TimeoutError

# Connection / availability errors that justify switching to DB fallback.
# ValueError/TypeError are API errors and must not trigger fallback.
_CACHE_CONN_ERRORS = (
    RedisConnectionError,
    RedisTimeoutError,
    ConnectionError,
    TimeoutError,
    OSError,
    socket.error,
)


class FallbackCache(BaseCache):
    """
    Allows you to set fallback cache backend (multiple cache backend).
    The data is not shared between cache backends.
    Example: Memcached is not available, backend switch to fallback.
    Site may slow down (cache have to be set) but will not rise an error.
    """

    _cache = None
    _cache_fallback = None

    def __init__(self, params=None, *args, **kwargs):
        BaseCache.__init__(self, *args, **kwargs)
        # TODO: Add backup cache backend as environment var
        self._cache = get_cache("redis")
        self._cache_fallback = get_cache("database")

    def add(self, key, value, timeout=None, version=None):
        return self._call_with_fallback(
            "add", key, value, timeout=timeout, version=version
        )

    def get(self, key, default=None, version=None):
        # On Redis miss, check DB fallback once — values may have been written
        # there during an outage (dual-write path) and must survive Redis recovery.
        try:
            result = self._call_main_cache(
                (key,), {"default": None, "version": version}, "get"
            )
        except (ValueError, TypeError):
            raise
        except Exception as e:
            Logger().info(
                logger,
                str(e),
                title="Switch to fallback database cache",
            )
            return self._call_fallback_cache(
                (key,), {"default": default, "version": version}, "get"
            )

        if result is not None:
            return result

        try:
            fb_result = self._call_fallback_cache(
                (key,), {"default": None, "version": version}, "get"
            )
            if fb_result is not None:
                return fb_result
        except Exception:
            pass
        return default

    def set(self, key, value, timeout=None, version=None, client=None):
        return self._call_with_fallback(
            "set", key, value, timeout=timeout, version=version
        )

    def touch(self, key, timeout=None, version=None):
        return self._call_with_fallback("touch", key, timeout, version=version)

    def get_many(self, keys, version=None):
        return self._call_with_fallback("get_many", keys, version=version)

    def has_key(self, key, version=None):
        return self._call_with_fallback("has_key", key, version=version)

    def set_many(self, data, timeout=None, version=None):
        return self._call_with_fallback(
            "set_many", data, timeout=timeout, version=version
        )

    def delete_many(self, keys, version=None):
        # Dual-delete so keys written during Redis outage are cleared from DB too.
        main_result = None
        try:
            main_result = self._call_main_cache((keys,), {"version": version}, "delete_many")
        except ValueError:
            raise
        except TypeError:
            raise
        except Exception as e:
            Logger().info(
                logger,
                str(e),
                title="Switch to fallback database cache",
            )
        try:
            fb_result = self._call_fallback_cache(
                (keys,), {"version": version}, "delete_many"
            )
            return main_result if main_result is not None else fb_result
        except Exception:
            return main_result

    def incr(self, key, delta=1, version=None):
        return self._call_with_fallback("incr", key, delta=delta, version=version)

    def decr(self, key, delta=1, version=None):
        return self._call_with_fallback("decr", key, delta=delta, version=version)

    def delete(self, key, version=None):
        # Dual-delete: remove from Redis and DB so version/list keys cannot linger
        # in the fallback after Redis recovers.
        main_ok = False
        try:
            main_ok = bool(
                self._call_main_cache((key,), {"version": version}, "delete")
            )
        except ValueError:
            raise
        except TypeError:
            raise
        except Exception as e:
            Logger().info(
                logger,
                str(e),
                title="Switch to fallback database cache",
            )
        fb_ok = False
        try:
            fb_ok = bool(
                self._call_fallback_cache((key,), {"version": version}, "delete")
            )
        except Exception:
            pass
        return main_ok or fb_ok

    def clear(self):
        # Attempt both backends so neither retains stale entries after recovery.
        main_err = None
        try:
            self._call_main_cache((), {}, "clear")
        except Exception as e:
            main_err = e
            Logger().info(
                logger,
                str(e),
                title="Switch to fallback database cache",
            )
        try:
            self._call_fallback_cache((), {}, "clear")
        except Exception as e:
            if main_err is not None:
                raise main_err from e

    def expire(self, key, timeout=None, version=None):
        """Proxy redis-only expire; DatabaseCache has no expire."""
        try:
            return self._cache.expire(key, timeout=timeout, version=version)
        except (ValueError, TypeError):
            raise
        except AttributeError:
            return False
        except _CACHE_CONN_ERRORS:
            try:
                return self._cache_fallback.touch(key, timeout, version=version)
            except Exception:
                return False
        except Exception:
            return False

    def pttl(self, key, version=None):
        """Proxy redis-only pttl; graceful None when unavailable."""
        try:
            return self._cache.pttl(key, version=version)
        except (ValueError, TypeError):
            raise
        except Exception:
            return None

    def keys(self, *args):
        r = self._cache
        try:
            return r.keys(args[0])
        except (ValueError, TypeError):
            raise
        except _CACHE_CONN_ERRORS:
            pattern = r"([^\s]*)"
            regex = args[0].replace("*", pattern)
            return list(
                CacheTable.objects.filter(cache_key__iregex=regex).values_list(
                    "cache_key", flat=True
                )
            )

    def _call_with_fallback(self, method, *args, **kwargs):
        try:
            return self._call_main_cache(args, kwargs, method)
        except (ValueError, TypeError):
            # Expected Django cache API behavior (e.g. incr/decr on a missing
            # key) or bad argument types. Must not be treated as a Redis outage.
            raise
        except Exception as e:
            Logger().info(
                logger,
                str(e),
                title="Switch to fallback database cache",
            )
            return self._call_fallback_cache(args, kwargs, method)

    def _call_main_cache(self, args, kwargs, method):
        return getattr(self._cache, method)(*args, **kwargs)

    def _call_fallback_cache(self, args, kwargs, method):
        return getattr(self._cache_fallback, method)(*args, **kwargs)
