from django.db import transaction
from django.db.models import F, Prefetch, QuerySet
from django.utils import timezone

from apps.products.models import (
    DiscountCampaign,
    Product,
    ProductImage,
    ProductVariant,
)


def get_running_campaign() -> DiscountCampaign | None:
    now = timezone.now()

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
            "category",
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


@transaction.atomic
def clear_special_offer_discounts() -> int:
    """
    Remove sale prices and special-offer flags from campaign members.
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

    return True


def schedule_campaign_end(*, campaign: DiscountCampaign) -> None:
    from apps.products.tasks import end_discount_campaign_task

    if campaign.ends_at is None:
        return

    campaign_id = campaign.id
    eta = campaign.ends_at

    transaction.on_commit(
        lambda: end_discount_campaign_task.apply_async(
            args=[campaign_id],
            eta=eta,
        )
    )
