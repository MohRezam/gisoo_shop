from django.db.models.signals import post_delete, post_save

from apps.shared.cache.list_cache import bump_cache_version
from apps.shared.cache import namespaces as ns


def register_home_cache_signals():
    from apps.home.models import (
        Banner,
        CustomerSatisfaction,
        FAQ,
        FAQCategory,
        HomeAbout,
        Slider,
    )

    mapping = {
        Banner: ns.HOME_BANNERS,
        Slider: ns.HOME_SLIDERS,
        HomeAbout: ns.HOME_ABOUT,
        CustomerSatisfaction: ns.HOME_SATISFACTION,
        FAQ: ns.HOME_FAQ,
        FAQCategory: ns.HOME_FAQ,
    }

    for model, namespace in mapping.items():

        def make_handler(ns_name):
            def handler(**_kwargs):
                bump_cache_version(ns_name)

            return handler

        handler = make_handler(namespace)
        post_save.connect(handler, sender=model, weak=False)
        post_delete.connect(handler, sender=model, weak=False)
