from django.core.cache import cache

TRACK_ORDER_TTL = 30  # seconds — short; status can change


def track_order_cache_key(code: str, phone: str) -> str:
    return f"orders:track:{code}:{phone}"


def get_cached_track_payload(code: str, phone: str):
    return cache.get(track_order_cache_key(code, phone))


def set_cached_track_payload(code: str, phone: str, payload: dict):
    cache.set(track_order_cache_key(code, phone), payload, TRACK_ORDER_TTL)


def invalidate_track_order_cache(code: str | None, phone: str | None):
    if code and phone:
        cache.delete(track_order_cache_key(code, phone))
