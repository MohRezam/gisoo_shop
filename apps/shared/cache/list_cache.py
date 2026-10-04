import hashlib
from urllib.parse import urlencode

from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response


DEFAULT_LIST_TTL = 60 * 5  # 5 minutes
DEFAULT_DETAIL_TTL = 60 * 10  # 10 minutes
DEFAULT_HOME_TTL = 60 * 10  # 10 minutes


def _version_key(namespace: str) -> str:
    return f"cache:ver:{namespace}"


def get_cache_version(namespace: str) -> int:
    value = cache.get(_version_key(namespace))
    if value is None:
        cache.set(_version_key(namespace), 1, timeout=None)
        return 1
    return int(value)


def bump_cache_version(namespace: str) -> int:
    key = _version_key(namespace)
    try:
        return cache.incr(key)
    except ValueError:
        cache.set(key, 2, timeout=None)
        return 2


def build_query_cache_key(namespace: str, request, extra: str = "") -> str:
    version = get_cache_version(namespace)
    params = request.query_params.copy()
    # stable order
    items = sorted((k, params.get(k)) for k in params.keys())
    query = urlencode(items, doseq=True)
    digest = hashlib.md5(f"{query}|{extra}".encode()).hexdigest()[:16]
    return f"{namespace}:v{version}:{digest}"


def build_detail_cache_key(namespace: str, lookup: str) -> str:
    version = get_cache_version(namespace)
    return f"{namespace}:detail:v{version}:{lookup}"


class CachedListMixin:
    """
    Cache GET list responses. Set:
      cache_namespace = "products:list"
      cache_ttl = 300
    """

    cache_namespace = "api:list"
    cache_ttl = DEFAULT_LIST_TTL

    def list(self, request, *args, **kwargs):
        key = build_query_cache_key(self.cache_namespace, request)
        cached = cache.get(key)
        if cached is not None:
            return Response(cached)

        response = super().list(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            cache.set(key, response.data, self.cache_ttl)
        return response


class CachedRetrieveMixin:
    """
    Cache GET detail responses. Set:
      cache_namespace = "products:detail"
      cache_ttl = 600
      cache_lookup_kwarg = "slug"  # or "pk"
    """

    cache_namespace = "api:detail"
    cache_ttl = DEFAULT_DETAIL_TTL
    cache_lookup_kwarg = None

    def retrieve(self, request, *args, **kwargs):
        lookup = self.cache_lookup_kwarg or getattr(self, "lookup_field", "pk")
        lookup_value = kwargs.get(lookup) or self.kwargs.get(lookup)
        key = build_detail_cache_key(self.cache_namespace, str(lookup_value))
        cached = cache.get(key)
        if cached is not None:
            return Response(cached)

        response = super().retrieve(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            cache.set(key, response.data, self.cache_ttl)
        return response


def cached_action_response(namespace: str, request, builder, ttl=DEFAULT_HOME_TTL, extra=""):
    """Helper for @action / APIView get that returns a Response payload dict."""
    key = build_query_cache_key(namespace, request, extra=extra)
    cached = cache.get(key)
    if cached is not None:
        return Response(cached)
    data = builder()
    cache.set(key, data, ttl)
    return Response(data)
