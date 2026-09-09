import factory

from apps.cart.models import Cart, CartItem
from apps.products.models import (
    Brand,
    Bundle,
    Category,
    Product,
    ProductVariant,
)


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    title = factory.Sequence(
        lambda n: f"Test Category {n}"
    )

    slug = factory.Sequence(
        lambda n: f"test-category-{n}"
    )


class BrandFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Brand

    title = factory.Sequence(
        lambda n: f"Test Brand {n}"
    )

    slug = factory.Sequence(
        lambda n: f"test-brand-{n}"
    )


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    category = factory.SubFactory(
        CategoryFactory
    )

    brand = factory.SubFactory(
        BrandFactory
    )

    title = factory.Sequence(
        lambda n: f"Test Product {n}"
    )

    slug = factory.Sequence(
        lambda n: f"test-product-{n}"
    )

    short_description = ""
    description = "Test product description"

    is_available = True


class ProductVariantFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = ProductVariant

    product = factory.SubFactory(
        ProductFactory
    )

    sku = factory.Sequence(
        lambda n: f"TEST-SKU-{n}"
    )

    price = 100_000

    discounted_price = None

    stock = 100

    volume = factory.Sequence(
        lambda n: n + 1
    )

    is_active = True


class BundleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Bundle

    variant = factory.SubFactory(
        ProductVariantFactory
    )

    title = factory.Sequence(
        lambda n: f"Test Bundle {n}"
    )

    description = ""

    quantity = 2

    price = 150_000

    is_active = True


class CartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cart

    is_active = True


class CartItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CartItem

    cart = factory.SubFactory(
        CartFactory
    )

    variant = factory.SubFactory(
        ProductVariantFactory
    )

    bundle = None

    quantity = 1