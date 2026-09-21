from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.shared.cache.list_cache import bump_cache_version
from apps.shared.cache import namespaces as ns


def _bump_product_caches(**_kwargs):
    for namespace in (
        ns.PRODUCTS_LIST,
        ns.PRODUCTS_DETAIL,
        ns.PRODUCTS_SPECIAL,
        ns.PRODUCTS_CONSULTATION,
    ):
        bump_cache_version(namespace)


def _connect(model, handler=_bump_product_caches):
    post_save.connect(handler, sender=model, weak=False)
    post_delete.connect(handler, sender=model, weak=False)


def register_product_cache_signals():
    from apps.products.models import (
        Brand,
        Bundle,
        Category,
        DiscountCampaign,
        HairProblem,
        HairType,
        Product,
        ProductImage,
        ProductVariant,
    )

    for model in (
        Product,
        ProductVariant,
        ProductImage,
        Brand,
        Category,
        HairProblem,
        HairType,
        Bundle,
        DiscountCampaign,
    ):
        _connect(model)

    # brand/category lists also
    def bump_taxonomies(**_kwargs):
        bump_cache_version(ns.PRODUCTS_BRANDS)
        bump_cache_version(ns.PRODUCTS_CATEGORIES)
        bump_cache_version(ns.PRODUCTS_HAIR_PROBLEMS)
        bump_cache_version(ns.PRODUCTS_HAIR_TYPES)
        bump_cache_version(ns.PRODUCTS_FILTERS_META)
        _bump_product_caches()

    for model in (Brand, Category, HairProblem, HairType):
        post_save.connect(bump_taxonomies, sender=model, weak=False)
        post_delete.connect(bump_taxonomies, sender=model, weak=False)

    def bump_filters_meta(**_kwargs):
        bump_cache_version(ns.PRODUCTS_FILTERS_META)
        _bump_product_caches()

    for model in (Product, ProductVariant):
        post_save.connect(bump_filters_meta, sender=model, weak=False)
        post_delete.connect(bump_filters_meta, sender=model, weak=False)
