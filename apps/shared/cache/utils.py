import typing

from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response


def cache_api_data(func):
    def inner(*args, **kwargs):
        func_self = args[0]
        if not has_function(func_self, "get_cache_key") or not has_function(
            func_self, "get_cache_ttl"
        ):
            raise Exception(
                'You need to define both "get_cache_key" and "get_cache_key" function for "cache_api_data" decorator.'
            )
        cache_key = func_self.get_cache_key()
        if not cache_key:
            return func(*args, **kwargs)
        cache_data = cache.get(cache_key)
        if cache_data is not None:
            return Response(cache_data)

        response = func(*args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            cache.set(cache_key, response.data, func_self.get_cache_ttl())
        return response

    return inner


def cache_class_data(func):
    def inner(*args, **kwargs):
        func_self = args[0]
        if not has_function(func_self, "get_cache_key") or not has_function(
            func_self, "get_cache_ttl"
        ):
            raise Exception(
                'You need to define both "get_cache_key" and "get_cache_key" function for "cache_class_data" decorator.'
            )
        cache_key = func_self.get_cache_key()
        cache_data = cache.get(cache_key)
        if cache_data is not None:
            return cache_data

        cache_data = func(*args, **kwargs)
        if cache_data is not None:
            cache.set(cache_key, cache_data, func_self.get_cache_ttl())
        return cache_data

    return inner


def has_function(obj, function_name):
    return callable(getattr(obj, function_name, None))


def delete_keys(keys: typing.List[str]):
    cache.delete_many(keys)


def list_keys_by_pattern(pattern: str):
    return cache.keys(pattern)


def make_key(key, key_prefix, version):
    return key
