from django.db.models.signals import post_delete, post_save

from apps.shared.cache.list_cache import bump_cache_version
from apps.shared.cache import namespaces as ns


def register_consultation_cache_signals():
    from apps.consultations.models import ConsultationFAQ

    def bump_faq_cache(**_kwargs):
        bump_cache_version(ns.CONSULTATIONS_FAQ)

    post_save.connect(bump_faq_cache, sender=ConsultationFAQ, weak=False)
    post_delete.connect(bump_faq_cache, sender=ConsultationFAQ, weak=False)
