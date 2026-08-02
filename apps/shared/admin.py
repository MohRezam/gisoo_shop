from admin_auto_filters.filters import AutocompleteFilterFactory
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django_admin_inline_paginator.admin import TabularInlinePaginated
from django_autoutils.admin_utils import AvatarAdmin, EditLinkAdmin
from django_object_actions import DjangoObjectActions
from jalali_date.admin import (
    ModelAdminJalaliMixin,
    StackedInlineJalaliMixin,
    TabularInlineJalaliMixin,
)


class BaseAdmin:
    exclude = ("creator",)


class CacheAwareModelAdmin:
    """
    Handle cache data
    """

    changelist_actions = ("invalidate_all_items_cache",)

    def invalidate_all_items_cache(self, request, queryset):
        pass

    def save_model(self, request, obj, form, change: bool):
        # noinspection PyUnresolvedReferences
        if "creator" in [f.name for f in obj._meta.fields]:
            if not obj.creator:
                obj.creator = request.user
        super().save_model(request, obj, form, change)
        self.invalidate_cache(obj, change)

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        self.invalidate_cache(obj, change=None)

    def delete_queryset(self, request, queryset):
        qs = list(queryset)
        super().delete_queryset(request, queryset)
        [self.invalidate_cache(obj, change=None) for obj in qs]

    def invalidate_cache(self, obj, change):
        pass


class BaseModelAdmin(
    ModelAdminJalaliMixin,
    DjangoObjectActions,
    AvatarAdmin,
    CacheAwareModelAdmin,
    BaseAdmin,
    admin.ModelAdmin,
):
    """
    Base admin for all models
    """

    changelist_actions = ("invalidate_all_items_cache",)

    def get_obj(self, obj):
        """
        Get not person object
        """
        if not obj:
            return None
        return self._get_obj(obj)

    # noinspection PyMethodMayBeStatic
    def _get_obj(self, obj):
        if hasattr(obj, "get_obj"):
            return obj.get_obj()
        return obj

    def _get_avatar_obj(self, obj):
        return self.get_obj(obj)


class BaseTabularInlineAdmin(
    TabularInlineJalaliMixin,
    AvatarAdmin,
    EditLinkAdmin,
    BaseAdmin,
    TabularInlinePaginated,
):
    """
    Base admin for all inlines
    """

    pass


class BaseStackedInlineAdmin(StackedInlineJalaliMixin, BaseTabularInlineAdmin):
    """
    Base admin for all inlines
    """

    template = "admin/edit_inline/stacked.html"


class BaseFavoriteAdminTable(BaseModelAdmin):
    """
    Base admin page for all favorite pages
    """

    exclude = None
    FIELD_NAME = ""
    avatar_field = "logo"

    search_fields = ["=id"]
    date_hierarchy = "modified_date"

    def _get_avatar_obj(self, obj):
        return getattr(obj, self.FIELD_NAME, None)

    def get_list_display(self, request):
        """
        Get list display
        """
        return [
            "id",
            "avatar_icon",
            "user",
            self.FIELD_NAME,
            "archived",
            "created_date",
            "modified_date",
        ]

    def get_list_filter(self, request):
        """
        Get list filter
        """
        return [
            AutocompleteFilterFactory("user", "user"),
            AutocompleteFilterFactory(self.FIELD_NAME, self.FIELD_NAME),
            "archived",
            "created_date",
            "modified_date",
        ]

    def get_autocomplete_fields(self, request):
        """
        Get autocomplete fields
        """
        return ["user", self.FIELD_NAME]

    def get_fields(self, request, obj=None):
        """
        Get fields for showing data in change page
        """
        return [
            ("id", "avatar_image"),
            "user",
            self.FIELD_NAME,
            "archived",
            ("created_date", "modified_date"),
        ]

    def get_readonly_fields(self, request, obj=None):
        """
        Add user and team to readonly field with obj has been saved
        """
        readonly_fields = ["id", "avatar_image", "created_date", "modified_date"]
        if obj:
            readonly_fields += ["user", self.FIELD_NAME]
        return readonly_fields


def linkify(field_name):
    """
    Converts a foreign key value into clickable links.

    If field_name is 'parent', link text will be str(obj.parent)
    Link will be admin url for the admin url for obj.parent.id: change
    """

    def _linkify(obj):
        linked_obj = getattr(obj, field_name)
        if linked_obj is None:
            return "-"
        app_label = linked_obj._meta.app_label
        model_name = linked_obj._meta.model_name
        view_name = f"admin: {app_label}_{model_name}_change"
        link_url = reverse(view_name, args=[linked_obj.pk])
        return format_html('<a href="{}">{}</a>', link_url, linked_obj)

    _linkify.short_description = field_name  # Sets column name
    return _linkify
