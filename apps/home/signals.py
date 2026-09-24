from django.db.models.signals import post_delete, post_save

from apps.shared.cache.list_cache import bump_cache_version
from apps.shared.cache import namespaces as ns


def register_home_cache_signals():
    from apps.home.models import (
        Banner,
        ContactFAQ,
        CustomerSatisfaction,
        FAQ,
        FAQCategory,
        HomeAbout,
        Slider,
        SocialLinks,
    )
    from apps.products.models import Category, Product

    mapping = {
        Banner: ns.HOME_BANNERS,
        Slider: ns.HOME_SLIDERS,
        HomeAbout: ns.HOME_ABOUT,
        CustomerSatisfaction: ns.HOME_SATISFACTION,
        FAQ: ns.HOME_FAQ,
        FAQCategory: ns.HOME_FAQ,
        ContactFAQ: ns.HOME_CONTACT_FAQ,
        SocialLinks: ns.HOME_SOCIAL_LINKS,
    }

    for model, namespace in mapping.items():

        def make_handler(ns_name):
            def handler(**_kwargs):
                bump_cache_version(ns_name)

            return handler

        handler = make_handler(namespace)
        post_save.connect(handler, sender=model, weak=False)
        post_delete.connect(handler, sender=model, weak=False)

    def bump_banner_slider_caches(**_kwargs):
        bump_cache_version(ns.HOME_BANNERS)
        bump_cache_version(ns.HOME_SLIDERS)

    for model in (Product, Category):
        # post_save: slug/title changes still referenced by banner/slider caches
        post_save.connect(bump_banner_slider_caches, sender=model, weak=False)
        post_delete.connect(bump_banner_slider_caches, sender=model, weak=False)
