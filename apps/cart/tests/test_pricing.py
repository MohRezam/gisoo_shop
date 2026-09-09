import pytest
from rest_framework.exceptions import ValidationError

from apps.cart.services.pricing import (
    calculate_cart_totals,
)

from .factories import (
    BundleFactory,
    CartFactory,
    CartItemFactory,
    ProductVariantFactory,
)
from apps.discounts.tests.factories import DiscountFactory
from ..services import apply_discount_to_cart


@pytest.mark.django_db
def test_cart_totals_without_discount():
    variant = ProductVariantFactory(
        price=100_000,
        discounted_price=None,
    )

    cart = CartFactory()

    CartItemFactory(
        cart=cart,
        variant=variant,
        quantity=2,
    )

    result = calculate_cart_totals(
        cart=cart,
        user=None,
        discount=None,
    )

    assert result["original_subtotal"] == 200_000
    assert result["product_discount"] == 0
    assert result["subtotal"] == 200_000
    assert result["coupon_discount"] == 0
    assert result["total"] == 200_000


@pytest.mark.django_db
def test_coupon_does_not_apply_to_discounted_products():
    discounted_variant = ProductVariantFactory(
        price=100_000,
        discounted_price=70_000,
    )

    regular_variant = ProductVariantFactory(
        price=50_000,
        discounted_price=None,
    )

    cart = CartFactory()

    CartItemFactory(
        cart=cart,
        variant=discounted_variant,
        quantity=1,
    )

    CartItemFactory(
        cart=cart,
        variant=regular_variant,
        quantity=1,
    )

    discount = DiscountFactory(
        discount_type="percentage",
        value=20,
        applies_to_discounted_products=False,
    )

    result = calculate_cart_totals(
        cart=cart,
        user=None,
        discount=discount,
    )

    assert result["original_subtotal"] == 150_000
    assert result["product_discount"] == 30_000
    assert result["subtotal"] == 120_000
    assert result["coupon_discount"] == 10_000
    assert result["total"] == 110_000


@pytest.mark.django_db
def test_coupon_applies_to_discounted_products():
    discounted_variant = ProductVariantFactory(
        price=100_000,
        discounted_price=70_000,
    )

    regular_variant = ProductVariantFactory(
        price=50_000,
        discounted_price=None,
    )

    cart = CartFactory()

    CartItemFactory(
        cart=cart,
        variant=discounted_variant,
        quantity=1,
    )

    CartItemFactory(
        cart=cart,
        variant=regular_variant,
        quantity=1,
    )

    discount = DiscountFactory(
        discount_type="percentage",
        value=20,
        applies_to_discounted_products=True,
    )

    result = calculate_cart_totals(
        cart=cart,
        user=None,
        discount=discount,
    )

    assert result["original_subtotal"] == 150_000
    assert result["product_discount"] == 30_000
    assert result["subtotal"] == 120_000
    assert result["coupon_discount"] == 24_000
    assert result["total"] == 96_000


@pytest.mark.django_db
def test_cart_totals_with_bundle():
    variant = ProductVariantFactory(
        price=100_000,
        discounted_price=None,
    )

    bundle = BundleFactory(
        variant=variant,
        quantity=2,
        price=150_000,
    )

    cart = CartFactory()

    CartItemFactory(
        cart=cart,
        variant=None,
        bundle=bundle,
        quantity=1,
    )

    result = calculate_cart_totals(
        cart=cart,
        user=None,
        discount=None,
    )

    assert result["original_subtotal"] == 200_000
    assert result["product_discount"] == 50_000
    assert result["subtotal"] == 150_000
    assert result["coupon_discount"] == 0
    assert result["total"] == 150_000


@pytest.mark.django_db
def test_coupon_does_not_apply_to_discounted_bundle():
    variant = ProductVariantFactory(
        price=100_000,
        discounted_price=None,
    )

    bundle = BundleFactory(
        variant=variant,
        quantity=2,
        price=150_000,
    )

    cart = CartFactory()

    CartItemFactory(
        cart=cart,
        variant=None,
        bundle=bundle,
        quantity=1,
    )

    discount = DiscountFactory(
        discount_type="percentage",
        value=20,
        applies_to_discounted_products=False,
    )

    result = calculate_cart_totals(
        cart=cart,
        user=None,
        discount=discount,
    )

    assert result["original_subtotal"] == 200_000
    assert result["product_discount"] == 50_000
    assert result["subtotal"] == 150_000
    assert result["coupon_discount"] == 0
    assert result["total"] == 150_000


@pytest.mark.django_db
def test_coupon_applies_to_discounted_bundle():
    variant = ProductVariantFactory(
        price=100_000,
        discounted_price=None,
    )

    bundle = BundleFactory(
        variant=variant,
        quantity=2,
        price=150_000,
    )

    cart = CartFactory()

    CartItemFactory(
        cart=cart,
        variant=None,
        bundle=bundle,
        quantity=1,
    )

    discount = DiscountFactory(
        discount_type="percentage",
        value=20,
        applies_to_discounted_products=True,
    )

    result = calculate_cart_totals(
        cart=cart,
        user=None,
        discount=discount,
    )

    assert result["original_subtotal"] == 200_000
    assert result["product_discount"] == 50_000
    assert result["subtotal"] == 150_000
    assert result["coupon_discount"] == 30_000
    assert result["total"] == 120_000


@pytest.mark.django_db
def test_coupon_rejects_cart_below_minimum_order_amount():
    variant = ProductVariantFactory(
        price=100_000,
        discounted_price=80_000,
    )

    cart = CartFactory()

    CartItemFactory(
        cart=cart,
        variant=variant,
        quantity=1,
    )

    discount = DiscountFactory(
        discount_type="percentage",
        value=20,
        minimum_order_amount=100_000,
    )

    with pytest.raises(ValidationError):
        calculate_cart_totals(
            cart=cart,
            user=None,
            discount=discount,
        )


@pytest.mark.django_db
def test_coupon_respects_maximum_discount_amount():
    variant = ProductVariantFactory(
        price=200_000,
        discounted_price=None,
    )

    cart = CartFactory()

    CartItemFactory(
        cart=cart,
        variant=variant,
        quantity=1,
    )

    discount = DiscountFactory(
        discount_type="percentage",
        value=20,
        maximum_discount_amount=25_000,
    )

    result = calculate_cart_totals(
        cart=cart,
        user=None,
        discount=discount,
    )

    assert result["original_subtotal"] == 200_000
    assert result["product_discount"] == 0
    assert result["subtotal"] == 200_000
    assert result["coupon_discount"] == 25_000
    assert result["total"] == 175_000


@pytest.mark.django_db
def test_fixed_coupon_cannot_exceed_eligible_price():
    variant = ProductVariantFactory(
        price=30_000,
        discounted_price=None,
    )

    cart = CartFactory()

    CartItemFactory(
        cart=cart,
        variant=variant,
        quantity=1,
    )

    discount = DiscountFactory(
        discount_type="fixed",
        value=50_000,
    )

    result = calculate_cart_totals(
        cart=cart,
        user=None,
        discount=discount,
    )

    assert result["original_subtotal"] == 30_000
    assert result["product_discount"] == 0
    assert result["subtotal"] == 30_000
    assert result["coupon_discount"] == 30_000
    assert result["total"] == 0


@pytest.mark.django_db
def test_cart_totals_with_multiple_quantity():
    variant = ProductVariantFactory(
        price=100_000,
        discounted_price=80_000,
    )

    cart = CartFactory()

    CartItemFactory(
        cart=cart,
        variant=variant,
        quantity=3,
    )

    discount = DiscountFactory(
        discount_type="percentage",
        value=10,
        applies_to_discounted_products=True,
    )

    result = calculate_cart_totals(
        cart=cart,
        user=None,
        discount=discount,
    )

    assert result["original_subtotal"] == 300_000
    assert result["product_discount"] == 60_000
    assert result["subtotal"] == 240_000
    assert result["coupon_discount"] == 24_000
    assert result["total"] == 216_000


@pytest.mark.django_db
def test_cart_totals_with_multiple_bundle_quantity():
    variant = ProductVariantFactory(
        price=100_000,
        discounted_price=None,
    )

    bundle = BundleFactory(
        variant=variant,
        quantity=2,
        price=150_000,
    )

    cart = CartFactory()

    CartItemFactory(
        cart=cart,
        variant=None,
        bundle=bundle,
        quantity=3,
    )

    discount = DiscountFactory(
        discount_type="percentage",
        value=10,
        applies_to_discounted_products=True,
    )

    result = calculate_cart_totals(
        cart=cart,
        user=None,
        discount=discount,
    )

    assert result["original_subtotal"] == 600_000
    assert result["product_discount"] == 150_000
    assert result["subtotal"] == 450_000
    assert result["coupon_discount"] == 45_000
    assert result["total"] == 405_000


@pytest.mark.django_db
def test_apply_discount_to_cart():
    variant = ProductVariantFactory(
        price=100_000,
        discounted_price=80_000,
    )

    cart = CartFactory()

    CartItemFactory(
        cart=cart,
        variant=variant,
        quantity=1,
    )

    discount = DiscountFactory(
        code="SAVE20",
        discount_type="percentage",
        value=20,
        applies_to_discounted_products=True,
    )

    result = apply_discount_to_cart(
        cart=cart,
        user=None,
        code="save20",
    )

    cart.refresh_from_db()

    assert cart.discount_id == discount.id

    assert result["discount"].id == discount.id
    assert result["original_subtotal"] == 100_000
    assert result["product_discount"] == 20_000
    assert result["subtotal"] == 80_000
    assert result["coupon_discount"] == 16_000
    assert result["total"] == 64_000