from django.contrib import admin
from django import forms
from django.db.models import Count
from django_admin_inline_paginator.admin import TabularInlinePaginated

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
                "یکی از فیلدهای «واریانت» یا «بسته» باید پر شود — نه هر دو و نه هیچ‌کدام."
            )

        return cleaned_data


class CartItemInline(TabularInlinePaginated):
    model = CartItem
    extra = 0
    per_page = 20
    pagination_key = "cartitem_page"

    fields = (
        "item_type",
        "variant",
        "bundle",
        "quantity",
    )

    readonly_fields = (
        "item_type",
    )

    raw_id_fields = ("variant", "bundle")

    @admin.display(description="نوع")
    def item_type(self, obj):
        if obj.bundle_id:
            return "بسته"

        if obj.variant_id:
            return "محصول"

        return "-"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
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

    exclude = ("creator", "archived")
    raw_id_fields = ("user", "discount")
    list_select_related = ("user", "discount")
    list_per_page = 15
    show_full_result_count = False

    inlines = (
        CartItemInline,
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(_items_count=Count("items"))
        )

    @admin.display(description="تعداد آیتم", ordering="_items_count")
    def items_count(self, obj):
        return obj._items_count


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Kept for advanced lookup; hidden from sidebar — manage via Cart."""

    form = CartItemAdminForm
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

    readonly_fields = (
        "created_at",
        "updated_at",
    )
    exclude = ("creator", "archived")
    raw_id_fields = ("cart", "variant", "bundle")
    list_select_related = (
        "cart",
        "variant",
        "variant__product",
        "bundle",
    )
    list_per_page = 15
    show_full_result_count = False
    list_display_links = ("cart",)

    def has_module_permission(self, request):
        return False

    @admin.display(description="نوع")
    def item_type(self, obj):
        if obj.bundle_id:
            return "بسته"

        if obj.variant_id:
            return "محصول"

        return "-"

    @admin.display(description="آیتم")
    def item_title(self, obj):
        if obj.bundle_id:
            return obj.bundle.title

        if obj.variant_id:
            return obj.variant.product.title

        return "-"
