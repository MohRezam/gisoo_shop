from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.users.models import User, UserPhoneNumber


class UserPhoneNumberInline(admin.TabularInline):
    model = UserPhoneNumber
    extra = 0
    fields = (
        "phone_number",
        "is_verified",
        "is_primary",
    )
    readonly_fields = (
        "is_verified",
    )


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = (
        "phone_number",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "is_staff",
        "is_active",
        "is_superuser",
    )

    search_fields = (
        "phone_number",
        "first_name",
        "last_name",
        "email",
        "phone_numbers__phone_number",
    )

    ordering = ("-id",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "phone_number",
                    "password",
                )
            },
        ),
        (
            "Personal information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "avatar",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Important dates",
            {
                "fields": (
                    "last_login",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "phone_number",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )

    exclude = ("creator",)

    inlines = (
        UserPhoneNumberInline,
    )