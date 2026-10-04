from django.contrib import admin

from apps.home.models import Banner, Slider


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "link_type",
        "display_order",
        "is_active",
        "created_at",
    )

    list_filter = (
        "link_type",
        "is_active",
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
    raw_id_fields = ("product", "category")
    list_per_page = 15
    list_display_links = ("link_type",)


@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "link_type",
        "custom_url",
        "display_order",
        "is_active",
        "created_at",
    )

    list_filter = (
        "link_type",
        "is_active",
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
    raw_id_fields = ("product", "category")
    list_per_page = 15
    list_display_links = ("link_type",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "image",
                    "link_type",
                    "product",
                    "category",
                    "custom_url",
                    "display_order",
                    "is_active",
                ),
                "description": (
                    "ابعاد پیشنهادی تصویر: ۱۹۲۰×۴۸۰ پیکسل (نسبت حدود ۴ به ۱). "
                    "برای لینک خارجی، نوع لینک را «لینک سفارشی / خارجی» بگذارید "
                    "و آدرس https را در «لینک سفارشی» وارد کنید."
                ),
            },
        ),
    )
