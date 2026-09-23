from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.discounts.models import (
    Discount,
    DiscountType,
    DiscountUsage,
)


def _pending_discount_reservations(*, discount, user=None):
    """
    Soft-reserved coupon uses: orders waiting for payment that
    already hold this discount but have not yet called
    register_discount_usage.
    """
    from apps.orders.models import Order, OrderStatus

    qs = Order.objects.filter(
        discount=discount,
        status=OrderStatus.WAITING_PAYMENT,
    )
    if user is not None:
        qs = qs.filter(user=user)
    return qs.count()


def calculate_discount(
    *,
    user,
    code,
    products_price,
    eligible_price=None,
    for_update=False,
    include_pending_reservations=False,
):
    """
    Validate discount code and calculate discount amount.

    products_price:
        Cart subtotal after product-level discounts.
        Used for minimum order validation.

    eligible_price:
        Amount that the coupon is allowed to discount.

    for_update:
        Lock the Discount row with select_for_update.

    include_pending_reservations:
        Count WAITING_PAYMENT orders that already hold this
        discount toward usage_limit / per_user_limit (soft reserve).

    Returns:
        {
            "discount": Discount,
            "discount_amount": int,
            "eligible_price": int,
        }
    """

    qs = Discount.objects.filter(
        code__iexact=code.strip(),
    )
    if for_update:
        qs = qs.select_for_update()

    discount = qs.first()

    if discount is None:
        raise ValidationError(
            "کد تخفیف نامعتبر میباشد"
        )

    if not discount.is_active:
        raise ValidationError(
            "کد تخفیف نامعتبر میباشد"
        )

    now = timezone.now()

    if discount.starts_at > now:
        raise ValidationError(
            "کد تخفیف نامعتبر میباشد"
        )

    if discount.expires_at < now:
        raise ValidationError(
            "کد تخفیف منقضی شده است"
        )

    effective_used = discount.used_count
    if include_pending_reservations:
        effective_used += _pending_discount_reservations(
            discount=discount,
        )

    if (
        discount.usage_limit > 0
        and effective_used >= discount.usage_limit
    ):
        raise ValidationError(
            "سقف استفاده از این کد تخفیف تکمیل شده است."
        )

    if products_price < discount.minimum_order_amount:
        raise ValidationError(
            "مبلغ سبد برای این کد تخفیف کافی نیست."
        )

    if (
        user
        and user.is_authenticated
        and discount.per_user_limit > 0
    ):
        user_usage_count = DiscountUsage.objects.filter(
            discount=discount,
            user=user,
        ).count()

        if include_pending_reservations:
            user_usage_count += _pending_discount_reservations(
                discount=discount,
                user=user,
            )

        if user_usage_count >= discount.per_user_limit:
            raise ValidationError(
                "شما قبلاً از این کد تخفیف استفاده کرده‌اید."
            )

    if eligible_price is None:
        eligible_price = products_price

    if discount.discount_type == DiscountType.PERCENTAGE:
        discount_amount = (
            eligible_price * discount.value
        ) // 100
    else:
        discount_amount = min(
            discount.value,
            eligible_price,
        )

    if (
        discount.maximum_discount_amount
        and discount_amount
        > discount.maximum_discount_amount
    ):
        discount_amount = discount.maximum_discount_amount

    discount_amount = min(
        discount_amount,
        eligible_price,
    )

    return {
        "discount": discount,
        "discount_amount": discount_amount,
        "eligible_price": eligible_price,
    }


@transaction.atomic
def register_discount_usage(*, discount, user, order):
    locked = (
        Discount.objects
        .select_for_update()
        .get(pk=discount.pk)
    )

    if (
        locked.usage_limit > 0
        and locked.used_count >= locked.usage_limit
    ):
        raise ValidationError(
            "سقف استفاده از این کد تخفیف تکمیل شده است."
        )

    if locked.per_user_limit > 0:
        user_usage_count = DiscountUsage.objects.filter(
            discount=locked,
            user=user,
        ).count()

        if user_usage_count >= locked.per_user_limit:
            raise ValidationError(
                "شما قبلاً از این کد تخفیف استفاده کرده‌اید."
            )

    usage, created = DiscountUsage.objects.get_or_create(
        discount=locked,
        user=user,
        order=order,
    )

    if created:
        Discount.objects.filter(id=locked.id).update(
            used_count=F("used_count") + 1,
        )

    return usage, created
