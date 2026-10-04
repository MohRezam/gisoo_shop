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
        category=None,
        categories=None,
        brand,
        title="Product",
        slug="product",
):
    product = Product.objects.create(
        brand=brand,
        title=title,
        slug=slug,
        description="Description",
        is_available=True,
    )
    cats = list(categories or [])
    if category is not None:
        cats.append(category)
    if cats:
        product.categories.set(cats)
    return product


def create_product_variant(
    product,
    sku,
    stock,
    price,
    discounted_price=None,
    volume=100,
):
    return ProductVariant.objects.create(
        product=product,
        sku=sku,
        stock=stock,
        price=price,
        discounted_price=discounted_price,
        volume=volume,
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
