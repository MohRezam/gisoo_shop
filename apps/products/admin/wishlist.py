from apps.products.models import (
    Wishlist,
    WishlistItem,
)
from django.contrib import admin


class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0
    exclude = ("creator",)
    raw_id_fields = ("product",)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """Support lookup; keep URL, hide from sidebar clutter."""

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
    exclude = ("creator", "archived")
    raw_id_fields = ("user",)
    list_per_page = 15
    show_full_result_count = False
    list_display_links = ("user",)

    def has_module_permission(self, request):
        return False
