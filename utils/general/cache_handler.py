from django.core.cache import cache


def expire_cache(partial_key):
    try:
        # Keys use colon separators: prefix:version:key (see make_key).
        keys = cache.keys(f"*:{partial_key}*")

        for key in keys:
            cache.delete(key)
        return True, None
    except (ValueError, Exception) as e:
        return False, e


def put_in_cache(key, value, exp_time=None):
    cache.set(key, value, timeout=exp_time)


def extend_cache(key, exp_time=None):
    expire = getattr(cache, "expire", None)
    if callable(expire):
        expire(key, timeout=exp_time)


def get_from_cache(key, delete=False):
    value = cache.get(key)
    if delete and value is not None:
        cache.delete(key)
    return value


def check_in_cache(key, value=None):
    in_cache_value = cache.get(key)
    if value:
        return in_cache_value == value
    return in_cache_value is not None


def get_cache_ttl(key):
    pttl = getattr(cache, "pttl", None)
    if callable(pttl):
        return pttl(key)
    return None


def remove_from_cache(key):
    cache.delete(key)
