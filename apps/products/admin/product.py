from django.contrib import admin

from apps.products.admin import BundleInline
from apps.products.models import (
    Attribute,
    AttributeValue,
    Product,
    ProductAttribute,
    ProductImage,
    ProductVariant,
    VariantAttribute, ProductRelatedProduct, DiscountCampaign,
)
import nested_admin
from django.db.models import F

class ProductImageInline(nested_admin.NestedTabularInline):
    model = ProductImage
    extra = 0
    exclude = ("creator", "archived")


class ProductAttributeInline(nested_admin.NestedTabularInline):
    model = ProductAttribute
    extra = 0
    exclude = ("creator", "archived")


class ProductVariantInline(nested_admin.NestedTabularInline):
    model = ProductVariant
    extra = 0

    inlines = [
        BundleInline,
    ]
    exclude = ("creator", "archived")


class VariantAttributeInline(admin.TabularInline):
    model = VariantAttribute
    extra = 0
    exclude = ("creator", "archived")


class ProductRelatedProductInline(nested_admin.NestedTabularInline):
    model = ProductRelatedProduct
    fk_name = "product"

    extra = 0

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
        "id",
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

    exclude = ("creator", "archived")
    raw_id_fields = ("category", "brand")
    list_per_page = 15

    inlines = [
        ProductImageInline,
        ProductAttributeInline,
        ProductVariantInline,
        ProductRelatedProductInline,
    ]


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

    exclude = ("creator", "archived")
    raw_id_fields = ("product",)
    list_per_page = 15


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
    exclude = ("creator", "archived")
    raw_id_fields = ("product",)
    list_per_page = 15


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
    exclude = ("creator", "archived")
    raw_id_fields = ("product", "attribute")
    list_per_page = 15


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
    exclude = ("creator", "archived")


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

    exclude = ("creator", "archived")


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

    exclude = ("creator", "archived")
    raw_id_fields = ("variant", "value")



@admin.register(DiscountCampaign)
class DiscountCampaignAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "starts_at",
        "ends_at",
        "is_active",
        "status",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "title",
    )

    filter_horizontal = (
        "products",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "status",
    )

    fieldsets = (
        (
            "اطلاعات کمپین",
            {
                "fields": (
                    "title",
                    "is_active",
                    "products",
                )
            },
        ),
        (
            "زمان‌بندی",
            {
                "fields": (
                    "starts_at",
                    "ends_at",
                )
            },
        ),
        (
            "وضعیت",
            {
                "fields": (
                    "status",
                )
            },
        ),
        (
            "اطلاعات سیستم",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    def formfield_for_manytomany(
        self,
        db_field,
        request,
        **kwargs,
    ):
        if db_field.name == "products":
            kwargs["queryset"] = Product.objects.filter(
                is_available=True,
                variants__is_active=True,
                variants__discounted_price__isnull=False,
                variants__discounted_price__lt=F(
                    "variants__price"
                ),
            ).distinct()

        return super().formfield_for_manytomany(
            db_field,
            request,
            **kwargs,
        )

    @admin.display(description="وضعیت")
    def status(self, obj):
        if obj.is_expired:
            return "منقضی شده"

        if obj.is_upcoming:
            return "در انتظار شروع"

        if obj.is_running:
            return "فعال"

        return "غیرفعال"

    def has_add_permission(self, request):
        return not DiscountCampaign.objects.exists()