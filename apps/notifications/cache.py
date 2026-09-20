from django.core.cache import cache

UNREAD_COUNT_TTL = 60 * 2  # 2 minutes


def unread_count_cache_key(user_id: int) -> str:
    return f"notifications:unread_count:user:{user_id}"


def get_cached_unread_count(user_id: int):
    return cache.get(unread_count_cache_key(user_id))


def set_cached_unread_count(user_id: int, count: int):
    cache.set(unread_count_cache_key(user_id), count, UNREAD_COUNT_TTL)


def invalidate_unread_count(user_id: int):
    cache.delete(unread_count_cache_key(user_id))
