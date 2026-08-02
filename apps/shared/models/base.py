"""
Shared models
"""

from django.core.cache import cache
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from apps.shared import cache as cache_keys


class BaseModel(models.Model):
    BASE_OBJECT = None

    created_date = models.DateTimeField(auto_now_add=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, null=True)
    creator = models.ForeignKey(
        to="users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_creator",
        verbose_name=_("creator"),
    )
    archived = models.BooleanField(default=False, verbose_name=_("archived"))

    class Meta:
        abstract = True
        ordering = ["-modified_date"]

    def generate(self, **kwargs):
        return

    def get_obj(self):
        """
        Get base object
        """
        if self.id is None:
            return None
        return self._get_obj()

    def _get_obj(self):
        if self.BASE_OBJECT is None:
            return self
        base_object = getattr(self, self.BASE_OBJECT, None)
        if base_object is None:
            return None
        get_base_obj = getattr(base_object, "get_obj", None)
        if get_base_obj is None:
            return base_object
        return get_base_obj()


class SearchableModel:
    @classmethod
    def search(
        cls,
        term,
        limit=5,
        fixed_filter_query=None,
        base_filter_query=None,
        extra_filter_query=None,
        cache_ttl=7 * 24 * 60 * 60,
    ):
        cache_key = cache_keys.get_football_term_search_key(term, cls.__name__)
        cache_result = cache.get(cache_key)
        if cache_result is not None:
            return cache_result
        if fixed_filter_query is None:
            fixed_filter_query = {}
        if base_filter_query is None:
            base_filter_query = Q(
                Q(name__icontains=term) | Q(translated_name__icontains=term)
            )
        if extra_filter_query is not None:
            if extra_filter_query["operator"] == "and":
                base_filter_query &= extra_filter_query["query"]
            else:
                base_filter_query |= extra_filter_query["query"]
        items = cls.objects.filter(base_filter_query, **fixed_filter_query).distinct()[
            :limit
        ]
        cache.set(cache_key, items, cache_ttl)
        return items


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
