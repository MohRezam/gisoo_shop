from django.contrib import admin, messages

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
        "show_in_special_offer",
        "created_at",
    )

    list_filter = (
        "category",
        "brand",
        "is_available",
        "show_in_special_offer",
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
    list_display_links = ("title",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "slug",
                    "category",
                    "brand",
                    "short_description",
                    "description",
                    "is_available",
                    "show_in_special_offer",
                    "hair_problems",
                    "hair_types",
                ),
            },
        ),
    )

    filter_horizontal = (
        "hair_problems",
        "hair_types",
    )

    inlines = [
        ProductImageInline,
        ProductAttributeInline,
        ProductVariantInline,
        ProductRelatedProductInline,
    ]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        product = form.instance
        if not product.show_in_special_offer:
            return

        if product.has_active_discount():
            return

        product.show_in_special_offer = False
        product.save(update_fields=["show_in_special_offer", "updated_at"])
        messages.error(
            request,
            "تیک پیشنهاد ویژه برداشته شد؛ محصول باید حداقل یک واریانت "
            "فعال با قیمت تخفیف‌خورده داشته باشد.",
        )


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        "id",
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
    list_display_links = ("sku", "product")


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
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
    list_display_links = ("product",)


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
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
    list_display_links = ("product",)


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
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
    list_per_page = 15
    list_display_links = ("name",)


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = (
        "id",
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
    list_per_page = 15
    list_display_links = ("attribute",)


@admin.register(VariantAttribute)
class VariantAttributeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
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
    list_per_page = 15
    list_display_links = ("variant",)


@admin.register(DiscountCampaign)
class DiscountCampaignAdmin(admin.ModelAdmin):
    list_display = (
        "id",
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
                ),
                "description": (
                    "محصولات را از صفحهٔ هر محصول با تیک "
                    "«نمایش در پیشنهاد ویژه» اضافه کنید."
                ),
            },
        ),
        (
            "زمان‌بندی",
            {
                "fields": (
                    "starts_at",
                    "ends_at",
                ),
                "description": (
                    "با رسیدن به زمان پایان، تخفیف محصولات عضو "
                    "پیشنهاد ویژه به‌صورت خودکار برداشته می‌شود."
                ),
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
    list_per_page = 15
    list_display_links = ("title",)

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
