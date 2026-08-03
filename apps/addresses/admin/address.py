from django.contrib import admin

from apps.addresses.models import Address
from apps.shared.admin import BaseModelAdmin


@admin.register(Address)
class AddressAdmin(BaseModelAdmin):
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