from celery import shared_task

from apps.products.services.discount_campaign import end_discount_campaign


@shared_task(name="apps.products.tasks.end_discount_campaign")
def end_discount_campaign_task(campaign_id: int):
    return end_discount_campaign(campaign_id=campaign_id)


@shared_task(name="apps.products.tasks.sweep_expired_discount_campaigns")
def sweep_expired_discount_campaigns():
    """
    Safety net if the scheduled end task was missed.
    Also clears orphan special-offer members when no campaign is running.
    """

    from apps.products.services.discount_campaign import (
        ensure_expired_campaigns_cleared,
    )

    return ensure_expired_campaigns_cleared()
