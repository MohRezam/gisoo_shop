from celery import shared_task
from django.utils import timezone

from apps.products.models import DiscountCampaign
from apps.products.services.discount_campaign import (
    end_discount_campaign,
)


@shared_task(name="apps.products.tasks.end_discount_campaign")
def end_discount_campaign_task(campaign_id: int):
    return end_discount_campaign(campaign_id=campaign_id)


@shared_task(name="apps.products.tasks.sweep_expired_discount_campaigns")
def sweep_expired_discount_campaigns():
    """
    Safety net if the eta-scheduled end task was missed.
    """

    now = timezone.now()

    expired_ids = list(
        DiscountCampaign.objects
        .filter(
            ends_at__lte=now,
            is_active=True,
        )
        .values_list("id", flat=True)
    )

    # Also catch campaigns already inactive but members still flagged
    # with discounts after a partial failure.
    from apps.products.models import Product

    has_stale_members = Product.objects.filter(
        show_in_special_offer=True,
    ).exists()

    if has_stale_members:
        stale_campaign_ids = list(
            DiscountCampaign.objects
            .filter(ends_at__lte=now)
            .values_list("id", flat=True)
        )
        expired_ids = list(set(expired_ids) | set(stale_campaign_ids))

    for campaign_id in expired_ids:
        end_discount_campaign_task.delay(campaign_id)

    return len(expired_ids)
