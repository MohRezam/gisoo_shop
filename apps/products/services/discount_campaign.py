from django.db import transaction
from django.db.models import F, Prefetch, QuerySet
from django.utils import timezone

from apps.products.models import (
    DiscountCampaign,
    Product,
    ProductImage,
    ProductVariant,
)
from apps.shared.cache.list_cache import bump_cache_version
from apps.shared.cache import namespaces as ns


def _running_campaign_at(now) -> DiscountCampaign | None:
    return (
        DiscountCampaign.objects
        .filter(
            is_active=True,
            starts_at__lte=now,
            ends_at__gt=now,
        )
        .order_by("-created_at")
        .first()
    )


def ensure_expired_campaigns_cleared() -> int:
    """
    Lazily end campaigns whose ends_at has passed.

    Called from storefront/cart/admin so discounts disappear even if
    Celery worker/beat missed the scheduled end task.
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

    if _running_campaign_at(now) is None:
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


def get_running_campaign() -> DiscountCampaign | None:
    ensure_expired_campaigns_cleared()
    return _running_campaign_at(timezone.now())


def discounted_variants_queryset() -> QuerySet[ProductVariant]:
    return ProductVariant.objects.filter(
        is_active=True,
        stock__gt=0,
        discounted_price__isnull=False,
        discounted_price__lt=F("price"),
    ).order_by("discounted_price")


def special_offer_products_queryset() -> QuerySet[Product]:
    """
    Products flagged for the special-offer section while a campaign is running.
    """

    if get_running_campaign() is None:
        return Product.objects.none()

    return (
        Product.objects
        .filter(
            show_in_special_offer=True,
            is_available=True,
            variants__is_active=True,
            variants__stock__gt=0,
            variants__discounted_price__isnull=False,
            variants__discounted_price__lt=F("variants__price"),
        )
        .select_related(
            "brand",
        )
        .prefetch_related(
            Prefetch(
                "images",
                queryset=ProductImage.objects.filter(
                    is_primary=True,
                ),
                to_attr="primary_images",
            ),
            Prefetch(
                "variants",
                queryset=discounted_variants_queryset(),
                to_attr="active_variants",
            ),
        )
        .distinct()
        .order_by("-created_at")
    )


def campaign_member_products_queryset() -> QuerySet[Product]:
    """Flagged special-offer products that still have a real discount."""

    return (
        Product.objects
        .filter(
            show_in_special_offer=True,
            is_available=True,
            variants__is_active=True,
            variants__discounted_price__isnull=False,
            variants__discounted_price__lt=F("variants__price"),
        )
        .distinct()
        .prefetch_related(
            Prefetch(
                "variants",
                queryset=ProductVariant.objects.filter(
                    is_active=True,
                    discounted_price__isnull=False,
                    discounted_price__lt=F("price"),
                ),
            ),
            Prefetch(
                "images",
                queryset=ProductImage.objects.filter(
                    is_primary=True,
                ),
            ),
        )
    )


def _bump_catalog_caches() -> None:
    """QuerySet.update() skips post_save; bump caches explicitly."""
    for namespace in (
        ns.PRODUCTS_LIST,
        ns.PRODUCTS_DETAIL,
        ns.PRODUCTS_SPECIAL,
        ns.PRODUCTS_CONSULTATION,
        ns.PRODUCTS_FILTERS_META,
    ):
        bump_cache_version(namespace)


@transaction.atomic
def clear_special_offer_discounts() -> int:
    """
    Remove sale prices and special-offer flags from campaign members.
    Restores each variant to its base ``price``.
    Returns the number of products cleared.
    """

    products = (
        Product.objects
        .select_for_update()
        .filter(show_in_special_offer=True)
    )
    product_ids = list(products.values_list("id", flat=True))

    if not product_ids:
        return 0

    ProductVariant.objects.filter(
        product_id__in=product_ids,
        discounted_price__isnull=False,
    ).update(discounted_price=None)

    updated = products.update(show_in_special_offer=False)
    _bump_catalog_caches()
    return updated


@transaction.atomic
def end_discount_campaign(*, campaign_id: int) -> bool:
    """
    End a campaign whose ends_at has passed: clear member discounts
    and deactivate the campaign. Idempotent.
    """

    campaign = (
        DiscountCampaign.objects
        .select_for_update()
        .filter(id=campaign_id)
        .first()
    )

    if campaign is None:
        return False

    now = timezone.now()

    if campaign.ends_at is None or campaign.ends_at > now:
        return False

    clear_special_offer_discounts()

    if campaign.is_active:
        campaign.is_active = False
        campaign.save(update_fields=["is_active", "updated_at"])
    else:
        # Campaign already inactive — still bump so stale sale prices leave CDN/cache.
        _bump_catalog_caches()

    return True


def schedule_campaign_end(*, campaign: DiscountCampaign) -> None:
    import logging

    from apps.products.tasks import end_discount_campaign_task

    if campaign.ends_at is None:
        return

    campaign_id = campaign.id
    # Countdown (seconds) is more reliable than eta across Celery timezones.
    delay = (campaign.ends_at - timezone.now()).total_seconds()
    logger = logging.getLogger(__name__)

    def _enqueue():
        try:
            if delay <= 0:
                end_discount_campaign_task.delay(campaign_id)
            else:
                end_discount_campaign_task.apply_async(
                    args=[campaign_id],
                    countdown=max(delay, 1),
                )
        except Exception:
            # Broker down: storefront/admin lazy clear still removes sales.
            logger.exception(
                "Failed to schedule end for discount campaign %s",
                campaign_id,
            )

    transaction.on_commit(_enqueue)
