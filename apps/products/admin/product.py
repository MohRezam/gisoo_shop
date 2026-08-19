from django.contrib import admin

from apps.products.admin import BundleInline
from apps.products.models import (
    Attribute,
    AttributeValue,
    Product,
    ProductAttribute,
    ProductImage,
    ProductVariant,
    VariantAttribute, ProductRelatedProduct,
)
from apps.shared.admin import BaseModelAdmin


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


class VariantAttributeInline(admin.TabularInline):
    model = VariantAttribute
    extra = 1


class ProductRelatedProductInline(admin.TabularInline):
    model = ProductRelatedProduct
    fk_name = "product"

    extra = 1

    autocomplete_fields = [
        "related_product",
    ]

    ordering = [
        "display_order",
    ]

    fields = [
        "related_product",
        "display_order",
    ]


@admin.register(Product)
class ProductAdmin(BaseModelAdmin):
    list_display = (
        "title",
        "category",
        "brand",
        "is_available",
        "created_at",
    )

    list_filter = (
        "category",
        "brand",
        "is_available",
        "created_at",
    )

    search_fields = (
        "title",
        "slug",
    )

    list_select_related = (
        "category",
        "brand",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }

    autocomplete_fields = [
        "category",
        "brand",
    ]

    inlines = [
        ProductImageInline,
        ProductAttributeInline,
        ProductVariantInline,
        BundleInline,
        ProductRelatedProductInline
    ]


@admin.register(ProductVariant)
class ProductVariantAdmin(BaseModelAdmin):
    list_display = (
        "sku",
        "product",
        "price",
        "discounted_price",
        "stock",
        "volume",
        "expiration_date",
        "is_active",
    )

    list_filter = (
        "is_active",
        "expiration_date",
    )

    list_editable = (
        "volume",
    )

    search_fields = (
        "sku",
        "product__title",
    )

    list_select_related = (
        "product",
    )

    inlines = [
        VariantAttributeInline,
    ]


@admin.register(ProductImage)
class ProductImageAdmin(BaseModelAdmin):
    list_display = (
        "product",
        "alt_text",
        "created_at",
    )

    search_fields = (
        "product__title",
        "alt_text",
    )

    list_select_related = (
        "product",
    )


@admin.register(ProductAttribute)
class ProductAttributeAdmin(BaseModelAdmin):
    list_display = (
        "product",
        "attribute",
        "value",
        "display_order",
        "created_at",
    )

    list_filter = (
        "attribute",
    )

    search_fields = (
        "product__title",
        "attribute__name",
        "value",
    )

    list_select_related = (
        "product",
        "attribute",
    )

    ordering = (
        "product",
        "display_order",
    )


@admin.register(Attribute)
class AttributeAdmin(BaseModelAdmin):
    list_display = (
        "name",
        "is_variant",
        "created_at",
    )

    list_filter = (
        "is_variant",
    )

    search_fields = (
        "name",
    )


@admin.register(AttributeValue)
class AttributeValueAdmin(BaseModelAdmin):
    list_display = (
        "attribute",
        "value",
        "created_at",
    )

    list_filter = (
        "attribute",
    )

    search_fields = (
        "value",
    )

    list_select_related = (
        "attribute",
    )


@admin.register(VariantAttribute)
class VariantAttributeAdmin(BaseModelAdmin):
    list_display = (
        "variant",
        "value",
        "created_at",
    )

    list_filter = (
        "value__attribute",
    )

    search_fields = (
        "variant__sku",
        "value__value",
    )

    list_select_related = (
        "variant",
        "value",
    )
