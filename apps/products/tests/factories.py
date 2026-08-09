from apps.products.models import (
    Brand,
    Category,
    Product,
    ProductImage,
    ProductVariant,
)


def create_category(
        *,
        title="Category",
        slug="category",
):
    return Category.objects.create(
        title=title,
        slug=slug,
    )


def create_brand(
        *,
        title="Brand",
        slug="brand",
):
    return Brand.objects.create(
        title=title,
        slug=slug,
    )


def create_product(
        *,
        category,
        brand,
        title="Product",
        slug="product",
):
    return Product.objects.create(
        category=category,
        brand=brand,
        title=title,
        slug=slug,
        description="Description",
        is_available=True,
    )


def create_product_variant(
        *,
        product,
        sku="sku-1",
        stock=10,
        price=100000,
):
    return ProductVariant.objects.create(
        product=product,
        sku=sku,
        price=price,
        stock=stock,
        is_active=True,
    )


def create_product_image(
        *,
        product,
        is_primary=True,
):
    return ProductImage.objects.create(
        product=product,
        is_primary=is_primary,
    )
