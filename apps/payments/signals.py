from django.db.models.signals import post_delete, post_save

from apps.shared.cache.list_cache import bump_cache_version
from apps.shared.cache import namespaces as ns


def register_payments_cache_signals():
    from apps.payments.models import PaymentGuideVideo

    def bump_guide(**_kwargs):
        bump_cache_version(ns.PAYMENT_GUIDE_VIDEO)

    post_save.connect(bump_guide, sender=PaymentGuideVideo, weak=False)
    post_delete.connect(bump_guide, sender=PaymentGuideVideo, weak=False)
