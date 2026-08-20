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
import nested_admin

class ProductImageInline(nested_admin.NestedTabularInline):
    model = ProductImage
    extra = 1
    exclude = ("creator",)


class ProductAttributeInline(nested_admin.NestedTabularInline):
    model = ProductAttribute
    extra = 1
    exclude = ("creator",)


class ProductVariantInline(nested_admin.NestedTabularInline):
    model = ProductVariant
    extra = 1

    inlines = [
        BundleInline,
    ]
    exclude = ("creator",)


class VariantAttributeInline(admin.TabularInline):
    model = VariantAttribute
    extra = 1
    exclude = ("creator",)


class ProductRelatedProductInline(nested_admin.NestedTabularInline):
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
class ProductAdmin(
    nested_admin.NestedModelAdmin,
    admin.ModelAdmin,
):
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
        ProductRelatedProductInline,
    ]
    exclude = ("creator", )


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
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
        BundleInline,
    ]

    exclude = ("creator",)

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
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
    exclude = ("creator", )

@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
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
    exclude = ("creator", )


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
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
    exclude = ("creator", )


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
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

    exclude = ("creator", )

@admin.register(VariantAttribute)
class VariantAttributeAdmin(admin.ModelAdmin):
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

    exclude = ("creator", )