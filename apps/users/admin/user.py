from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Permission

from apps.shared.admin_filters import PersianBooleanFilter
from apps.users.admin.forms import GisooUserPasswordChangeForm
from apps.users.models import User, UserPhoneNumber


class UserPhoneNumberInlineForm(forms.ModelForm):
    class Meta:
        model = UserPhoneNumber
        fields = (
            "phone_number",
            "is_verified",
            "is_primary",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = self.instance
        if instance and instance.pk and instance.is_verified:
            self.fields["phone_number"].disabled = True


class UserPhoneNumberInline(admin.TabularInline):
    model = UserPhoneNumber
    form = UserPhoneNumberInlineForm
    extra = 0
    fields = (
        "phone_number",
        "is_verified",
        "is_primary",
    )
    readonly_fields = ("is_verified",)
    verbose_name = "شماره تلفن"
    verbose_name_plural = "شماره‌های تلفن"
    show_change_link = False


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    change_password_form = GisooUserPasswordChangeForm
    change_user_password_template = "admin/users/user/change_password.html"

    list_display = (
        "phone_number",
        "first_name",
        "last_name",
        "email",
        "is_staff",
        "is_active",
        "created_at",
    )
    list_display_links = ("phone_number", "first_name")
    list_filter = (
        ("is_staff", PersianBooleanFilter),
        ("is_active", PersianBooleanFilter),
        ("is_superuser", PersianBooleanFilter),
    )
    search_fields = (
        "phone_number",
        "first_name",
        "last_name",
        "email",
    )
    search_help_text = "جستجو بر اساس شماره، نام، نام خانوادگی یا ایمیل"
    ordering = ("-id",)
    list_per_page = 25
    list_max_show_all = 100
    show_full_result_count = False
    preserve_filters = True
    save_on_top = True

    # Avoid loading every Permission into a dual-list widget.
    filter_horizontal = ("groups",)
    autocomplete_fields = ("user_permissions",)

    readonly_fields = ("last_login", "created_at")

    fieldsets = (
        (
            "حساب کاربری",
            {
                "fields": (
                    "phone_number",
                    "password",
                ),
            },
        ),
        (
            "اطلاعات شخصی",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "birthdate",
                    "avatar",
                ),
            },
        ),
        (
            "دسترسی‌ها",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            "تاریخ‌ها",
            {
                "classes": ("collapse",),
                "fields": (
                    "last_login",
                    "created_at",
                ),
            },
        ),
    )

    add_fieldsets = (
        (
            "ایجاد کاربر",
            {
                "classes": ("wide",),
                "fields": (
                    "phone_number",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )

    exclude = ("creator",)
    inlines = (UserPhoneNumberInline,)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Changelist does not need avatar file fields.
        match = getattr(request, "resolver_match", None)
        if match and str(getattr(match, "url_name", "")).endswith("_changelist"):
            return qs.defer("avatar")
        return qs


if not admin.site.is_registered(Permission):

    @admin.register(Permission)
    class PermissionAdmin(admin.ModelAdmin):
        search_fields = (
            "name",
            "codename",
            "content_type__app_label",
            "content_type__model",
        )
        list_display = ("name", "codename", "content_type")
        list_select_related = ("content_type",)
        list_per_page = 30
        show_full_result_count = False
        ordering = ("content_type__app_label", "codename")
