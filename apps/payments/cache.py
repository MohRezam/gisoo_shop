from django.core.cache import cache

DESTINATION_CARD_CACHE_KEY = "payments:destination_card:active:v1"
DESTINATION_CARD_CACHE_TTL = 60 * 10  # 10 minutes

PAYMENT_INTENT_TOKEN_TTL = 60  # short cache for public token lookup


def payment_intent_token_cache_key(token: str) -> str:
    return f"payments:intent:token:{token}"


def get_cached_destination_card_id():
    return cache.get(DESTINATION_CARD_CACHE_KEY)


def set_cached_destination_card_id(card_id: int):
    cache.set(DESTINATION_CARD_CACHE_KEY, card_id, DESTINATION_CARD_CACHE_TTL)


def invalidate_destination_card_cache():
    cache.delete(DESTINATION_CARD_CACHE_KEY)


def get_cached_payment_intent_payload(token: str):
    return cache.get(payment_intent_token_cache_key(token))


def set_cached_payment_intent_payload(token: str, payload: dict):
    cache.set(payment_intent_token_cache_key(token), payload, PAYMENT_INTENT_TOKEN_TTL)


def invalidate_payment_intent_token_cache(token: str):
    cache.delete(payment_intent_token_cache_key(token))
