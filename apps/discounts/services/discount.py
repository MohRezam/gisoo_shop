from django.db.models import F
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from apps.discounts.models import (
    Discount,
    DiscountType,
    DiscountUsage,
)


def calculate_discount(
    *,
    user,
    code,
    products_price,
    eligible_price=None,
):
    """
    Validate discount code and calculate discount amount.

    products_price:
        Cart subtotal after product-level discounts.
        Used for minimum order validation.

    eligible_price:
        Amount that the coupon is allowed to discount.

    Returns:
        {
            "discount": Discount,
            "discount_amount": int,
            "eligible_price": int,
        }
    """

    discount = Discount.objects.filter(
        code=code.upper(),
    ).first()

    if discount is None:
        raise ValidationError(
            _("Discount code not found.")
        )

    if not discount.is_active:
        raise ValidationError(
            _("Discount code is inactive.")
        )

    now = timezone.now()

    if discount.starts_at > now:
        raise ValidationError(
            _("Discount code has not started yet.")
        )

    if discount.expires_at < now:
        raise ValidationError(
            _("Discount code has expired.")
        )

    if (
        discount.usage_limit > 0
        and discount.used_count >= discount.usage_limit
    ):
        raise ValidationError(
            _("Discount usage limit reached.")
        )

    if products_price < discount.minimum_order_amount:
        raise ValidationError(
            _(
                "Minimum order amount is %(amount)s."
            ) % {
                "amount": discount.minimum_order_amount,
            }
        )

    if user and user.is_authenticated:
        user_usage_count = DiscountUsage.objects.filter(
            discount=discount,
            user=user,
        ).count()

        if user_usage_count >= discount.per_user_limit:
            raise ValidationError(
                _("You have already used this discount.")
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


def register_discount_usage(
    *,
    discount,
    user,
    order,
):
    DiscountUsage.objects.create(
        discount=discount,
        user=user,
        order=order,
    )

    Discount.objects.filter(
        id=discount.id,
    ).update(
        used_count=F("used_count") + 1,
    )