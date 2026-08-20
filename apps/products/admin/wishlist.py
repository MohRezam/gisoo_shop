from apps.products.models import (
    Wishlist,
    WishlistItem,
)
from django.contrib import admin



class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0
    exclude = ("creator",)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
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
    exclude = ("creator",)
