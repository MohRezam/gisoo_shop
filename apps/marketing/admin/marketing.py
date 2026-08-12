from django.contrib import admin

from apps.marketing.models import MarketingSubscriber


@admin.register(MarketingSubscriber)
class MarketingSubscriberAdmin(admin.ModelAdmin):
    list_display = (
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