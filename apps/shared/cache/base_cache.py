import logging

from django.core.cache.backends.base import BaseCache

from apps.shared.models.db_cache import CacheTable
from apps.shared.utils import get_cache
from utils.general.logger import Logger

logging.basicConfig()
logger = logging.getLogger("custom")


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
        return self._call_with_fallback("get", key, default=default, version=version)

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
        return self._call_with_fallback("delete_many", keys, version=version)

    def incr(self, key, delta=1, version=None):
        return self._call_with_fallback("incr", key, delta=delta, version=version)

    def decr(self, key, delta=1, version=None):
        return self._call_with_fallback("decr", key, delta=delta, version=version)

    def delete(self, key, version=None):
        return self._call_with_fallback("delete", key, version=version)

    def clear(self):
        return self._call_with_fallback("clear")

    def keys(self, *args):
        r = self._cache
        try:
            return r.keys(args[0])
        except:  # noqa: E722
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
