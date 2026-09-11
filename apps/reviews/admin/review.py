from django.contrib import admin

from apps.reviews.models import ProductReview


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "user",
        "rating",
        "status",
        "is_featured",
        "homepage_order",
        "created_at",
    )

    list_filter = (
        "status",
        "is_featured",
        "rating",
        "created_at",
    )

    search_fields = (
        "product__title",
        "comment",
    )

    list_editable = (
        "status",
        "is_featured",
        "homepage_order",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )