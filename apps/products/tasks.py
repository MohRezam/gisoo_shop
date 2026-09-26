from celery import shared_task
from django.utils import timezone

from apps.products.models import DiscountCampaign, Product
from apps.products.services.discount_campaign import (
    clear_special_offer_discounts,
    end_discount_campaign,
    get_running_campaign,
)


@shared_task(name="apps.products.tasks.end_discount_campaign")
def end_discount_campaign_task(campaign_id: int):
    return end_discount_campaign(campaign_id=campaign_id)


@shared_task(name="apps.products.tasks.sweep_expired_discount_campaigns")
def sweep_expired_discount_campaigns():
    """
    Safety net if the eta-scheduled end task was missed.
    Also clears orphan special-offer members when no campaign is running.
    """

    now = timezone.now()

    expired_ids = list(
        DiscountCampaign.objects
        .filter(ends_at__lte=now)
        .values_list("id", flat=True)
    )

    ended = 0
    for campaign_id in expired_ids:
        if end_discount_campaign(campaign_id=campaign_id):
            ended += 1

    # Orphan members: flag still on after campaign deleted / clear failed.
    if get_running_campaign() is None:
        has_upcoming = DiscountCampaign.objects.filter(
            is_active=True,
            starts_at__gt=now,
        ).exists()
        has_stale_members = Product.objects.filter(
            show_in_special_offer=True,
        ).exists()
        if has_stale_members and not has_upcoming:
            clear_special_offer_discounts()

    return ended
