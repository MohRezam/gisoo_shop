from django.contrib import admin

from apps.products.models import Bundle

import nested_admin


class BundleInline(nested_admin.NestedTabularInline):
    model = Bundle
    extra = 0
    verbose_name = "بسته"
    verbose_name_plural = "بسته‌ها"

    fields = (
        "title",
        "quantity",
        "price",
        "is_active",
        "display_order",
    )
    exclude = ("creator", "archived")


@admin.register(Bundle)
class BundleAdmin(admin.ModelAdmin):
    """Managed via Product → Variant inlines; hidden from sidebar."""

    list_display = (
        "id",
        "title",
        "variant",
        "quantity",
        "price",
        "is_active",
        "display_order",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "title",
        "variant__sku",
        "variant__product__title",
    )

    list_editable = (
        "display_order",
        "is_active",
    )

    ordering = (
        "display_order",
        "-created_at",
    )
    exclude = ("creator", "archived")
    raw_id_fields = ("variant",)
    list_per_page = 15
    show_full_result_count = False
    list_display_links = ("title",)
    list_select_related = ("variant", "variant__product")

    def has_module_permission(self, request):
        return False
