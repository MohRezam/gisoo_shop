from django.db.models.signals import post_delete, post_save

from apps.shared.cache.list_cache import bump_cache_version
from apps.shared.cache import namespaces as ns


def register_magazine_cache_signals():
    from apps.magazine.models import Magazine, MagazineCategory

    def bump(**_kwargs):
        for namespace in (
            ns.MAGAZINE_LIST,
            ns.MAGAZINE_DETAIL,
            ns.MAGAZINE_HOME,
            ns.MAGAZINE_ALL,
        ):
            bump_cache_version(namespace)

    for model in (Magazine, MagazineCategory):
        post_save.connect(bump, sender=model, weak=False)
        post_delete.connect(bump, sender=model, weak=False)
