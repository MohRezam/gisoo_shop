from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.shipping.cache import invalidate_shipping_methods_cache
from apps.shipping.models import ShippingMethod


@receiver(post_save, sender=ShippingMethod)
@receiver(post_delete, sender=ShippingMethod)
def clear_shipping_methods_cache(sender, **kwargs):
    invalidate_shipping_methods_cache()
