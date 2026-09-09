from unittest.mock import patch

import pytest
from rest_framework.exceptions import ValidationError

from apps.discounts.services.discount import calculate_discount

from .factories import DiscountFactory, UserFactory
from datetime import timedelta
from django.utils import timezone
from apps.discounts.models import DiscountType


@pytest.mark.django_db
class TestCalculateDiscountUsageLimit:

    def test_unlimited_discount_is_allowed(self):
        discount = DiscountFactory(
            usage_limit=0,
            used_count=100,
        )

        result = calculate_discount(
            user=None,
            code=discount.code,
            products_price=100_000,
        )

        assert result["discount"] == discount
        assert result["discount_amount"] == 10_000

    def test_discount_is_rejected_when_usage_limit_is_reached(self):
        discount = DiscountFactory(
            usage_limit=10,
            used_count=10,
        )

        with pytest.raises(ValidationError) as exc_info:
            calculate_discount(
                user=None,
                code=discount.code,
                products_price=100_000,
            )

        assert "usage limit" in str(
            exc_info.value
        ).lower()

    def test_discount_is_allowed_when_usage_limit_is_not_reached(self):
        discount = DiscountFactory(
            usage_limit=10,
            used_count=9,
        )

        result = calculate_discount(
            user=None,
            code=discount.code,
            products_price=100_000,
        )

        assert result["discount_amount"] == 10_000


@pytest.mark.django_db
class TestCalculateDiscountPerUserLimit:

    @patch(
        "apps.discounts.services.discount.DiscountUsage.objects.filter"
    )
    def test_user_cannot_use_discount_more_than_per_user_limit(
            self,
            mock_filter,
    ):
        user = UserFactory()

        discount = DiscountFactory(
            per_user_limit=1,
        )

        mock_filter.return_value.count.return_value = 1

        with pytest.raises(ValidationError) as exc_info:
            calculate_discount(
                user=user,
                code=discount.code,
                products_price=100_000,
            )

        assert "already used" in str(
            exc_info.value
        ).lower()

        mock_filter.assert_called_once_with(
            discount=discount,
            user=user,
        )

    @patch(
        "apps.discounts.services.discount.DiscountUsage.objects.filter"
    )
    def test_user_can_use_discount_if_limit_is_not_reached(
            self,
            mock_filter,
    ):
        user = UserFactory()

        discount = DiscountFactory(
            per_user_limit=2,
        )

        mock_filter.return_value.count.return_value = 1

        result = calculate_discount(
            user=user,
            code=discount.code,
            products_price=100_000,
        )

        assert result["discount_amount"] == 10_000

        mock_filter.assert_called_once_with(
            discount=discount,
            user=user,
        )

    @patch(
        "apps.discounts.services.discount.DiscountUsage.objects.filter"
    )
    def test_different_user_can_use_same_discount(
            self,
            mock_filter,
    ):
        user = UserFactory()

        discount = DiscountFactory(
            per_user_limit=1,
        )

        mock_filter.return_value.count.return_value = 0

        result = calculate_discount(
            user=user,
            code=discount.code,
            products_price=100_000,
        )

        assert result["discount_amount"] == 10_000

        mock_filter.assert_called_once_with(
            discount=discount,
            user=user,
        )


@pytest.mark.django_db
class TestCalculateDiscountValidity:

    def test_inactive_discount_is_rejected(self):
        discount = DiscountFactory(
            is_active=False,
        )

        with pytest.raises(ValidationError) as exc_info:
            calculate_discount(
                user=None,
                code=discount.code,
                products_price=100_000,
            )

        assert "inactive" in str(
            exc_info.value
        ).lower()

    def test_discount_that_has_not_started_is_rejected(self):
        discount = DiscountFactory(
            starts_at=timezone.now() + timedelta(days=1),
        )

        with pytest.raises(ValidationError) as exc_info:
            calculate_discount(
                user=None,
                code=discount.code,
                products_price=100_000,
            )

        assert "not started" in str(
            exc_info.value
        ).lower()

    def test_expired_discount_is_rejected(self):
        discount = DiscountFactory(
            starts_at=timezone.now() - timedelta(days=7),
            expires_at=timezone.now() - timedelta(days=1),
        )

        with pytest.raises(ValidationError) as exc_info:
            calculate_discount(
                user=None,
                code=discount.code,
                products_price=100_000,
            )

        assert "expired" in str(
            exc_info.value
        ).lower()


@pytest.mark.django_db
class TestCalculateDiscountAmount:

    def test_percentage_discount(self):
        discount = DiscountFactory(
            discount_type=DiscountType.PERCENTAGE,
            value=20,
        )

        result = calculate_discount(
            user=None,
            code=discount.code,
            products_price=100_000,
        )

        assert result["discount_amount"] == 20_000

    def test_fixed_discount(self):
        discount = DiscountFactory(
            discount_type=DiscountType.FIXED,
            value=15_000,
        )

        result = calculate_discount(
            user=None,
            code=discount.code,
            products_price=100_000,
        )

        assert result["discount_amount"] == 15_000

    def test_fixed_discount_cannot_exceed_eligible_price(self):
        discount = DiscountFactory(
            discount_type=DiscountType.FIXED,
            value=150_000,
        )

        result = calculate_discount(
            user=None,
            code=discount.code,
            products_price=100_000,
        )

        assert result["discount_amount"] == 100_000

    def test_maximum_discount_amount_limits_percentage_discount(self):
        discount = DiscountFactory(
            discount_type=DiscountType.PERCENTAGE,
            value=20,
            maximum_discount_amount=10_000,
        )

        result = calculate_discount(
            user=None,
            code=discount.code,
            products_price=100_000,
        )

        assert result["discount_amount"] == 10_000

    def test_eligible_price_limits_coupon_discount(self):
        discount = DiscountFactory(
            discount_type=DiscountType.PERCENTAGE,
            value=20,
        )

        result = calculate_discount(
            user=None,
            code=discount.code,
            products_price=100_000,
            eligible_price=30_000,
        )

        assert result["eligible_price"] == 30_000
        assert result["discount_amount"] == 6_000


@pytest.mark.django_db
class TestCalculateDiscountMinimumOrder:

    def test_discount_is_rejected_below_minimum_order_amount(self):
        discount = DiscountFactory(
            minimum_order_amount=100_000,
        )

        with pytest.raises(ValidationError) as exc_info:
            calculate_discount(
                user=None,
                code=discount.code,
                products_price=99_999,
            )

        assert "minimum order amount" in str(
            exc_info.value
        ).lower()

    def test_discount_is_allowed_at_minimum_order_amount(self):
        discount = DiscountFactory(
            minimum_order_amount=100_000,
        )

        result = calculate_discount(
            user=None,
            code=discount.code,
            products_price=100_000,
        )

        assert result["discount_amount"] == 10_000
