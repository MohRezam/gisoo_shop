from django.db import transaction
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from apps.shared.cache.list_cache import bump_cache_version
from apps.shared.cache import namespaces as ns


def register_consultation_cache_signals():
    from apps.consultations.models import ConsultationFAQ

    def bump_faq_cache(**_kwargs):
        bump_cache_version(ns.CONSULTATIONS_FAQ)

    post_save.connect(bump_faq_cache, sender=ConsultationFAQ, weak=False)
    post_delete.connect(bump_faq_cache, sender=ConsultationFAQ, weak=False)


@receiver(pre_save, sender="consultations.ConsultationRequest")
def _store_previous_consultation_status(sender, instance, **kwargs):
    if not instance.pk:
        instance._previous_status = None
        return
    instance._previous_status = (
        sender.objects
        .filter(pk=instance.pk)
        .values_list("status", flat=True)
        .first()
    )


@receiver(post_save, sender="consultations.ConsultationRequest")
def _notify_user_when_consultation_answered(sender, instance, created, **kwargs):
    """
    When employer marks a request as completed, SMS (+ in-app) the customer.
    """
    from apps.consultations.models.consultation import ConsultationRequest

    if created:
        return

    previous = getattr(instance, "_previous_status", None)
    if instance.status != ConsultationRequest.Status.COMPLETED:
        return
    if previous == ConsultationRequest.Status.COMPLETED:
        return

    phone = (instance.phone_number or "").strip()
    if not phone:
        return

    consultation_id = str(instance.pk)
    user_id = instance.user_id
    user = instance.user

    def _notify():
        from apps.notifications.models import InAppNotificationType
        from apps.notifications.services.inbox import notify_user
        from apps.notifications.tasks import send_consultation_answered_sms

        send_consultation_answered_sms.delay(
            user_id=user_id,
            recipient=phone,
            consultation_id=consultation_id,
        )

        if user is not None:
            notify_user(
                user=user,
                title="پاسخ مشاوره آماده است",
                body=(
                    "کارشناس به درخواست مشاوره شما پاسخ داده است. "
                    "می‌توانید نتیجه را در حساب کاربری ببینید."
                ),
                type=InAppNotificationType.SYSTEM,
                link=f"/account/consultations/{consultation_id}",
            )

    transaction.on_commit(_notify)
