from django.contrib import admin

from apps.addresses.models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "title",
        "city",
        "is_default",
        "created_at",
    )

    list_filter = (
        "city",
        "province",
        "is_default",
    )

    search_fields = (
        "user__phone_number",
        "receiver_name",
        "postal_code",
    )
    exclude = ("creator",)
