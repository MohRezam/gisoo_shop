from django.contrib import admin
from django import forms
from apps.cart.models import Cart, CartItem


class CartItemAdminForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()

        variant = cleaned_data.get("variant")
        bundle = cleaned_data.get("bundle")

        if (variant is None) == (bundle is None):
            raise forms.ValidationError(
                "Select either a variant or a bundle."
            )

        return cleaned_data


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

    fields = (
        "item_type",
        "variant",
        "bundle",
        "quantity",
    )

    readonly_fields = (
        "item_type",
    )

    autocomplete_fields = (
        "variant",
        "bundle",
    )

    def item_type(self, obj):
        if obj.bundle_id:
            return "Bundle"

        if obj.variant_id:
            return "Product"

        return "-"

    item_type.short_description = "Type"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    form = CartItemAdminForm
    list_display = (
        "uuid",
        "user",
        "is_active",
        "items_count",
        "created_at",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    search_fields = (
        "uuid",
        "user__username",
        "user__phone_number",
    )

    readonly_fields = (
        "uuid",
        "created_at",
        "updated_at",
    )

    autocomplete_fields = (
        "user",
    )

    inlines = (
        CartItemInline,
    )

    def items_count(self, obj):
        return obj.items.count()

    items_count.short_description = "Items"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cart",
        "item_type",
        "item_title",
        "quantity",
        "created_at",
    )

    list_filter = (
        "created_at",
    )

    search_fields = (
        "cart__uuid",
        "variant__sku",
        "variant__product__title",
        "bundle__title",
    )

    autocomplete_fields = (
        "cart",
        "variant",
        "bundle",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    def item_type(self, obj):
        if obj.bundle_id:
            return "Bundle"

        if obj.variant_id:
            return "Product"

        return "-"

    item_type.short_description = "Type"

    def item_title(self, obj):
        if obj.bundle_id:
            return obj.bundle.title

        if obj.variant_id:
            return obj.variant.product.title

        return "-"

    item_title.short_description = "Item"
