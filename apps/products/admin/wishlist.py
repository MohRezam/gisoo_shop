from apps.products.models import (
    Attribute,
    AttributeValue,
    Product,
    ProductAttribute,
    ProductImage,
    ProductVariant,
    VariantAttribute,
    Wishlist,
    WishlistItem,
)
from django.contrib import admin

from apps.shared.admin import BaseModelAdmin


class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0


@admin.register(Wishlist)
class WishlistAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "user",
        "guest_token",
        "created_at",
    )

    search_fields = (
        "user__phone_number",
        "user__email",
        "guest_token",
    )

    list_select_related = (
        "user",
    )

    inlines = [
        WishlistItemInline,
    ]