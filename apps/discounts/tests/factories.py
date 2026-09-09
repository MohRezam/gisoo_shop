from datetime import timedelta

import factory
from django.utils import timezone

from apps.discounts.models import Discount, DiscountType
from apps.users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    phone_number = factory.Sequence(
        lambda n: f"0912000{n:04d}"
    )


class DiscountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Discount

    code = factory.Sequence(
        lambda n: f"TEST{n}"
    )

    discount_type = DiscountType.PERCENTAGE
    value = 10

    minimum_order_amount = 0
    maximum_discount_amount = None

    applies_to_discounted_products = True

    usage_limit = 0
    used_count = 0

    per_user_limit = 1

    starts_at = factory.LazyFunction(
        timezone.now
    )

    expires_at = factory.LazyFunction(
        lambda: timezone.now() + timedelta(days=7)
    )

    is_active = True