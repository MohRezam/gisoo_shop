from django.db.models.signals import m2m_changed, post_delete, post_save

from apps.shared.cache.list_cache import bump_cache_version
from apps.shared.cache import namespaces as ns


def register_magazine_cache_signals():
    from apps.magazine.models import Magazine, MagazineCategory
    from apps.products.models import Product, ProductVariant

    def bump(**_kwargs):
        for namespace in (
            ns.MAGAZINE_LIST,
            ns.MAGAZINE_DETAIL,
            ns.MAGAZINE_HOME,
            ns.MAGAZINE_ALL,
        ):
            bump_cache_version(namespace)

    def bump_detail(**_kwargs):
        bump_cache_version(ns.MAGAZINE_DETAIL)

    for model in (Magazine, MagazineCategory, Product, ProductVariant):
        post_save.connect(bump, sender=model, weak=False)
        post_delete.connect(bump, sender=model, weak=False)

    # M2M edits do not fire Magazine post_save; invalidate detail cache explicitly.
    m2m_changed.connect(
        bump_detail,
        sender=Magazine.related_products.through,
        weak=False,
    )
    m2m_changed.connect(
        bump_detail,
        sender=Magazine.related_articles.through,
        weak=False,
    )
