from django.contrib import admin

from apps.marketing.models import MarketingSubscriber


@admin.register(MarketingSubscriber)
class MarketingSubscriberAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "phone_number",
        "is_subscribed",
        "subscribed_at",
        "unsubscribed_at",
    )

    list_filter = (
        "is_subscribed",
    )

    search_fields = (
        "phone_number",
    )

    ordering = (
        "-subscribed_at",
    )
    exclude = ("creator", "archived")
    list_per_page = 15
    list_display_links = ("phone_number",)
