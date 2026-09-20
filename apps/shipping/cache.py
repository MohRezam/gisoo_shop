from django.core.cache import cache

SHIPPING_METHODS_CACHE_KEY = "shipping:methods:active:v1"
SHIPPING_METHODS_CACHE_TTL = 60 * 5  # 5 minutes


def get_cached_shipping_methods():
    return cache.get(SHIPPING_METHODS_CACHE_KEY)


def set_cached_shipping_methods(payload):
    cache.set(SHIPPING_METHODS_CACHE_KEY, payload, SHIPPING_METHODS_CACHE_TTL)


def invalidate_shipping_methods_cache():
    cache.delete(SHIPPING_METHODS_CACHE_KEY)
