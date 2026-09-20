from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.payments.cache import invalidate_destination_card_cache
from apps.payments.models import PaymentDestinationCard


@receiver(post_save, sender=PaymentDestinationCard)
@receiver(post_delete, sender=PaymentDestinationCard)
def clear_destination_card_cache(sender, **kwargs):
    invalidate_destination_card_cache()
