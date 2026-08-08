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
):
    """
    Validate discount code and calculate discount amount.

    Returns:
        {
            "discount": Discount,
            "discount_amount": Decimal,
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
            and
            discount.used_count >= discount.usage_limit
    ):
        raise ValidationError(
            _("Discount usage limit reached.")
        )

    if (
            products_price <
            discount.minimum_order_amount
    ):
        raise ValidationError(
            _(
                "Minimum order amount is %(amount)s."
            ) % {
                "amount": discount.minimum_order_amount,
            }
        )

    user_usage_count = DiscountUsage.objects.filter(
        discount=discount,
        user=user,
    ).count()

    if (
            user_usage_count >=
            discount.per_user_limit
    ):
        raise ValidationError(
            _("You have already used this discount.")
        )

    if (
            discount.discount_type ==
            DiscountType.PERCENTAGE
    ):
        discount_amount = (
                                  products_price *
                                  discount.value
                          ) // 100

    else:
        discount_amount = discount.value

    if (
            discount.maximum_discount_amount
            and
            discount_amount >
            discount.maximum_discount_amount
    ):
        discount_amount = (
            discount.maximum_discount_amount
        )

    if discount_amount > products_price:
        discount_amount = products_price

    return {
        "discount": discount,
        "discount_amount": discount_amount,
    }


def register_discount_usage(
        *,
        discount,
        user,
        order,
):
    """
    Register successful discount usage.
    """

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
