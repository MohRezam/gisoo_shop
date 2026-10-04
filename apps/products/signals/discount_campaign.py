from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.products.models import DiscountCampaign, ProductVariant
from apps.products.services.discount_campaign import (
    schedule_campaign_end,
)


@receiver(post_save, sender=DiscountCampaign)
def schedule_discount_campaign_end(
    sender,
    instance: DiscountCampaign,
    **kwargs,
):
    if instance.ends_at is None:
        return

    schedule_campaign_end(campaign=instance)


def _sync_special_offer_flag_for_product(product):
    if product is None:
        return

    if not product.show_in_special_offer:
        return

    if product.has_active_discount():
        return

    product.show_in_special_offer = False
    product.save(update_fields=["show_in_special_offer", "updated_at"])


@receiver(post_save, sender=ProductVariant)
def unset_special_offer_when_discount_removed(
    sender,
    instance: ProductVariant,
    **kwargs,
):
    # A variant that itself carries a valid discount must not clear the
    # flag mid-save while other inlines are still being written.
    if (
        instance.is_active
        and instance.discounted_price is not None
        and instance.price is not None
        and instance.discounted_price < instance.price
    ):
        return

    _sync_special_offer_flag_for_product(instance.product)


@receiver(post_delete, sender=ProductVariant)
def unset_special_offer_when_variant_deleted(
    sender,
    instance: ProductVariant,
    **kwargs,
):
    product = getattr(instance, "product", None)
    if product is None and instance.product_id:
        from apps.products.models import Product

        product = Product.objects.filter(id=instance.product_id).first()

    _sync_special_offer_flag_for_product(product)
