from django.contrib import admin
from django.urls import reverse

from apps.magazine.models import MagazineCategory, Magazine
from apps.shared.widgets import GisooRichTextWidget
from apps.shared.admin_filters import (
    PersianBooleanFilter,
    PersianRelatedFilter,
)


@admin.register(MagazineCategory)
class MagazineCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "slug",
    )
    search_fields = (
        "name",
    )
    prepopulated_fields = {
        "slug": ("name",),
    }
    exclude = ("creator", "archived")
    list_per_page = 15
    list_display_links = ("name",)


@admin.register(Magazine)
class MagazineAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "category",
        "published_at",
        "is_published",
        "is_featured",
        "reading_time",
    )

    list_filter = (
        ("category", PersianRelatedFilter),
        ("is_published", PersianBooleanFilter),
        ("is_featured", PersianBooleanFilter),
    )

    search_fields = (
        "title",
        "short_description",
        "content",
    )

    prepopulated_fields = {
        "slug": ("title",),
    }

    raw_id_fields = (
        "category",
        "related_products",
        "related_articles",
    )

    exclude = ("creator", "archived")
    list_per_page = 15
    list_display_links = ("title",)
    list_select_related = ("category",)
    show_full_result_count = False

    fieldsets = (
        (
            "محتوای مقاله",
            {
                "fields": (
                    "title",
                    "slug",
                    "category",
                    "short_description",
                    "content",
                    "thumbnail",
                ),
                "description": "عنوان، متن و تصویر اصلی مقاله را اینجا وارد کنید.",
            },
        ),
        (
            "انتشار",
            {
                "fields": (
                    "published_at",
                    "is_published",
                    "is_featured",
                    "reading_time",
                ),
                "description": (
                    "منتشر شده را روشن کنید تا مقاله اجازهٔ نمایش داشته باشد. "
                    "اگر تاریخ انتشار در آینده باشد، تا همان ساعت در سایت دیده نمی‌شود. "
                    "مقاله ویژه فقط یکی می‌تواند باشد و بالای صفحهٔ مجله نشان داده می‌شود."
                ),
            },
        ),
        (
            "ارتباطات",
            {
                "classes": ("collapse",),
                "fields": (
                    "related_products",
                    "related_articles",
                ),
                "description": "محصولات و مقالات مرتبط برای پیشنهاد به کاربر.",
            },
        ),
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "published_at":
            kwargs["help_text"] = (
                "ساعت نمایش در سایت. اگر این زمان نرسیده باشد، حتی با روشن بودن «منتشر شده» مقاله مخفی می‌ماند."
            )
        elif db_field.name == "is_published":
            kwargs["help_text"] = (
                "خاموش یعنی پیش‌نویس و در سایت نیست. روشن یعنی از زمان تاریخ انتشار به بعد در مجله دیده می‌شود."
            )
        elif db_field.name == "is_featured":
            kwargs["help_text"] = (
                "مقالهٔ برجستهٔ بالای صفحهٔ مجله. فقط یک مقاله ویژه می‌ماند؛ با انتخاب این، ویژهٔ قبلی برداشته می‌شود."
            )
        elif db_field.name == "content":
            kwargs["widget"] = GisooRichTextWidget(
                attrs={"data-upload-url": reverse("admin-richtext-image")}
            )
            kwargs["help_text"] = (
                "سبک متن را از منوی بالای کادر انتخاب کنید. "
                "ابزار جدول فقط داخل جدول، و اندازهٔ عکس فقط وقتی عکس انتخاب شده باشد، دیده می‌شود."
            )
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if obj.is_featured:
            Magazine.objects.exclude(
                pk=obj.pk
            ).filter(
                is_featured=True
            ).update(
                is_featured=False
            )

        super().save_model(request, obj, form, change)
