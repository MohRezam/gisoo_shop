from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from jalali_date.admin import ModelAdminJalaliMixin
from nested_admin.formsets import NestedInlineFormSet

from apps.products.admin import BundleInline
from apps.products.models import (
    Attribute,
    AttributeValue,
    Product,
    ProductAttribute,
    ProductFAQ,
    ProductImage,
    ProductVariant,
    VariantAttribute, ProductRelatedProduct, DiscountCampaign,
)
from utils.helpers.jalali_helper import get_persian_jalali_from_datetime
import nested_admin


class ProductImageInlineFormSet(NestedInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        primary_count = 0
        image_count = 0

        for form in self.forms:
            if not hasattr(form, "cleaned_data") or not form.cleaned_data:
                continue
            if self.can_delete and form.cleaned_data.get("DELETE"):
                continue

            image = form.cleaned_data.get("image")
            has_image = bool(image)
            if (
                not has_image
                and form.instance.pk
                and getattr(form.instance, "image", None)
            ):
                has_image = True

            if not has_image and not form.instance.pk:
                continue

            if has_image:
                image_count += 1

            if form.cleaned_data.get("is_primary"):
                primary_count += 1

        if image_count == 0:
            return

        if primary_count == 0:
            raise ValidationError(
                "دقیقاً یک تصویر باید به‌عنوان تصویر اصلی انتخاب شود."
            )
        if primary_count > 1:
            raise ValidationError(
                "بیش از یک تصویر اصلی مجاز نیست؛ دقیقاً یک تصویر را اصلی کنید."
            )


class ProductImageInline(nested_admin.NestedTabularInline):
    model = ProductImage
    formset = ProductImageInlineFormSet
    extra = 0
    exclude = ("creator", "archived")
    verbose_name = "تصویر"
    verbose_name_plural = "تصاویر محصول (دقیقاً یک تصویر اصلی)"


class ProductAttributeInline(nested_admin.NestedTabularInline):
    model = ProductAttribute
    extra = 0
    exclude = ("creator", "archived")
    raw_id_fields = ("attribute",)


class ProductFAQInline(nested_admin.NestedTabularInline):
    model = ProductFAQ
    extra = 0
    max_num = 6
    fields = (
        "question",
        "answer",
        "is_active",
        "ordering",
    )
    ordering = (
        "ordering",
        "id",
    )
    verbose_name = "سوال متداول"
    verbose_name_plural = "سوالات متداول محصول (حداکثر ۶ مورد)"


class ProductVariantInline(nested_admin.NestedTabularInline):
    model = ProductVariant
    extra = 0
    verbose_name = "تنوع محصول"
    verbose_name_plural = "تنوع‌های محصول"

    inlines = [
        BundleInline,
    ]
    exclude = ("creator", "archived")
    fields = (
        "sku",
        "price",
        "discounted_price",
        "stock",
        "volume",
        "expiration_date",
        "display_order",
        "is_active",
    )


class VariantAttributeInline(admin.TabularInline):
    model = VariantAttribute
    extra = 0
    exclude = ("creator", "archived")
    raw_id_fields = ("value",)


class ProductRelatedProductInline(nested_admin.NestedTabularInline):
    model = ProductRelatedProduct
    fk_name = "product"

    extra = 0

    raw_id_fields = ("related_product",)

    ordering = [
        "display_order",
    ]

    fields = [
        "related_product",
        "display_order",
    ]


@admin.register(Product)
class ProductAdmin(
    nested_admin.NestedModelAdmin,
    admin.ModelAdmin,
):
    list_display = (
        "id",
        "title",
        "brand",
        "is_available",
        "is_gisoo_recommended",
        "recommended_order",
        "show_in_special_offer",
        "created_at",
    )

    list_filter = (
        "is_available",
        "is_gisoo_recommended",
        "show_in_special_offer",
        "created_at",
    )

    search_fields = (
        "title",
        "slug",
        "brand__title",
    )

    list_select_related = (
        "brand",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }

    exclude = ("creator", "archived")
    raw_id_fields = (
        "categories",
        "brand",
        "hair_problems",
        "hair_types",
    )
    list_per_page = 15
    show_full_result_count = False
    list_display_links = ("title",)

    list_editable = (
        "is_gisoo_recommended",
        "recommended_order",
    )

    def changelist_view(self, request, extra_context=None):
        from apps.products.services.discount_campaign import (
            ensure_expired_campaigns_cleared,
        )

        ensure_expired_campaigns_cleared()
        return super().changelist_view(request, extra_context=extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        from apps.products.services.discount_campaign import (
            ensure_expired_campaigns_cleared,
        )

        ensure_expired_campaigns_cleared()
        return super().change_view(
            request,
            object_id,
            form_url=form_url,
            extra_context=extra_context,
        )

    fieldsets = (
        (
            "اطلاعات اصلی",
            {
                "description": (
                    "عنوان و توضیحات محصول در فروشگاه. "
                    "دسته‌بندی اختیاری است و می‌توان چند دسته انتخاب کرد. "
                    "برند، دسته، مشکل مو و نوع مو را با آیکون ذره‌بین "
                    "از روی شناسه انتخاب کنید."
                ),
                "fields": (
                    "title",
                    "slug",
                    "categories",
                    "brand",
                    "short_description",
                    "description",
                    "is_available",
                    "hair_problems",
                    "hair_types",
                ),
            },
        ),
        (
            "نمایش در فروشگاه",
            {
                "description": (
                    "پیشنهاد ویژه = کمپین تخفیف. "
                    "پیشنهادی گیسو = فیلتر «پیشنهادی گیسو سنتر»."
                ),
                "fields": (
                    "show_in_special_offer",
                    "is_gisoo_recommended",
                    "recommended_order",
                ),
            },
        ),
    )

    inlines = [
        ProductImageInline,
        ProductAttributeInline,
        ProductVariantInline,
        ProductRelatedProductInline,
        ProductFAQInline,
    ]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        product = form.instance
        want_special = bool(form.cleaned_data.get("show_in_special_offer"))

        # Re-read after inlines (and any post_save signals) settled.
        product.refresh_from_db(fields=["show_in_special_offer"])

        if not want_special:
            # Leaving the campaign: restore base price only if it was a member.
            was_member = product.show_in_special_offer
            if was_member:
                product.show_in_special_offer = False
                product.save(
                    update_fields=["show_in_special_offer", "updated_at"]
                )
                cleared = product.variants.filter(
                    discounted_price__isnull=False,
                ).update(discounted_price=None)
                if cleared:
                    messages.info(
                        request,
                        "محصول از پیشنهاد ویژه خارج شد و قیمت تخفیف‌خورده "
                        "واریانت‌ها به قیمت اصلی برگشت.",
                    )
            return

        if product.has_active_discount():
            if not product.show_in_special_offer:
                product.show_in_special_offer = True
                product.save(update_fields=["show_in_special_offer", "updated_at"])
            return

        if product.show_in_special_offer:
            product.show_in_special_offer = False
            product.save(update_fields=["show_in_special_offer", "updated_at"])

        messages.error(
            request,
            "تیک پیشنهاد ویژه اعمال نشد؛ محصول باید حداقل یک واریانت "
            "فعال با «قیمت تخفیف‌خورده» کمتر از قیمت اصلی داشته باشد. "
            "تخفیف واریانت را در همین فرم پر کنید و دوباره ذخیره کنید.",
        )


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "sku",
        "product",
        "price",
        "discounted_price",
        "stock",
        "volume",
        "display_order",
        "expiration_date",
        "is_active",
    )

    list_editable = (
        "display_order",
        "is_active",
        "volume",
    )

    list_filter = (
        "is_active",
        "expiration_date",
    )

    search_fields = (
        "sku",
        "product__title",
    )

    list_select_related = (
        "product",
    )

    inlines = [
        VariantAttributeInline,
        BundleInline,
    ]

    exclude = ("creator", "archived")
    raw_id_fields = ("product",)
    list_per_page = 15
    show_full_result_count = False
    list_display_links = ("sku", "product")


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Managed via Product inlines; hidden from sidebar."""

    list_display = (
        "id",
        "product",
        "alt_text",
        "created_at",
    )

    search_fields = (
        "product__title",
        "alt_text",
    )

    list_select_related = (
        "product",
    )
    exclude = ("creator", "archived")
    raw_id_fields = ("product",)
    list_per_page = 15
    show_full_result_count = False
    list_display_links = ("product",)

    def has_module_permission(self, request):
        return False


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    """Managed via Product inlines; hidden from sidebar."""

    list_display = (
        "id",
        "product",
        "attribute",
        "value",
        "display_order",
        "created_at",
    )

    list_filter = (
        "attribute",
    )

    search_fields = (
        "product__title",
        "attribute__name",
        "value",
    )

    list_select_related = (
        "product",
        "attribute",
    )

    ordering = (
        "product",
        "display_order",
    )
    exclude = ("creator", "archived")
    raw_id_fields = ("product", "attribute")
    list_per_page = 15
    show_full_result_count = False
    list_display_links = ("product",)

    def has_module_permission(self, request):
        return False


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "is_variant",
        "created_at",
    )

    list_filter = (
        "is_variant",
    )

    search_fields = (
        "name",
    )
    exclude = ("creator", "archived")
    list_per_page = 15
    list_display_links = ("name",)


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "attribute",
        "value",
        "created_at",
    )

    list_filter = (
        "attribute",
    )

    search_fields = (
        "value",
    )

    list_select_related = (
        "attribute",
    )

    exclude = ("creator", "archived")
    raw_id_fields = ("attribute",)
    list_per_page = 15
    list_display_links = ("attribute",)


@admin.register(VariantAttribute)
class VariantAttributeAdmin(admin.ModelAdmin):
    """Managed via ProductVariant inlines; hidden from sidebar."""

    list_display = (
        "id",
        "variant",
        "value",
        "created_at",
    )

    list_filter = (
        "value__attribute",
    )

    search_fields = (
        "variant__sku",
        "value__value",
    )

    list_select_related = (
        "variant",
        "value",
    )

    exclude = ("creator", "archived")
    raw_id_fields = ("variant", "value")
    list_per_page = 15
    show_full_result_count = False
    list_display_links = ("variant",)

    def has_module_permission(self, request):
        return False


@admin.register(DiscountCampaign)
class DiscountCampaignAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "starts_at_fa",
        "ends_at_fa",
        "is_active",
        "status",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "title",
    )

    readonly_fields = (
        "created_at_fa",
        "updated_at_fa",
        "status",
    )

    fieldsets = (
        (
            "اطلاعات کمپین",
            {
                "fields": (
                    "title",
                    "is_active",
                ),
                "description": (
                    "محصولات را از صفحهٔ هر محصول با تیک "
                    "«نمایش در پیشنهاد ویژه» اضافه کنید."
                ),
            },
        ),
        (
            "زمان‌بندی (شمسی)",
            {
                "fields": (
                    "starts_at",
                    "ends_at",
                ),
                "description": (
                    "تاریخ را از تقویم شمسی انتخاب کنید. "
                    "با رسیدن به زمان پایان، تخفیف محصولات عضو "
                    "پیشنهاد ویژه به‌صورت خودکار برداشته می‌شود."
                ),
            },
        ),
        (
            "وضعیت",
            {
                "fields": (
                    "status",
                )
            },
        ),
        (
            "اطلاعات سیستم",
            {
                "fields": (
                    "created_at_fa",
                    "updated_at_fa",
                )
            },
        ),
    )
    list_per_page = 15
    list_display_links = ("title",)

    @admin.display(description="شروع (شمسی)", ordering="starts_at")
    def starts_at_fa(self, obj):
        return get_persian_jalali_from_datetime(obj.starts_at)

    @admin.display(description="پایان (شمسی)", ordering="ends_at")
    def ends_at_fa(self, obj):
        return get_persian_jalali_from_datetime(obj.ends_at)

    @admin.display(description="ایجاد (شمسی)")
    def created_at_fa(self, obj):
        return get_persian_jalali_from_datetime(obj.created_at)

    @admin.display(description="آخرین ویرایش (شمسی)")
    def updated_at_fa(self, obj):
        return get_persian_jalali_from_datetime(obj.updated_at)

    @admin.display(description="وضعیت")
    def status(self, obj):
        if obj.is_expired:
            return "منقضی شده"

        if obj.is_upcoming:
            return "در انتظار شروع"

        if obj.is_running:
            return "فعال"

        return "غیرفعال"

    def changelist_view(self, request, extra_context=None):
        from apps.products.services.discount_campaign import (
            ensure_expired_campaigns_cleared,
        )

        ensure_expired_campaigns_cleared()
        return super().changelist_view(request, extra_context=extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        from apps.products.services.discount_campaign import (
            ensure_expired_campaigns_cleared,
        )

        ensure_expired_campaigns_cleared()
        return super().change_view(
            request,
            object_id,
            form_url=form_url,
            extra_context=extra_context,
        )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        from django.utils import timezone

        from apps.products.services.discount_campaign import (
            end_discount_campaign,
        )

        # If end time is already past (or just set to past), clear discounts now
        # so we do not wait only on Celery.
        if obj.pk and obj.ends_at and obj.ends_at <= timezone.now():
            ended = end_discount_campaign(campaign_id=obj.pk)
            if ended:
                messages.success(
                    request,
                    "زمان کمپین گذشته بود؛ تخفیف محصولات عضو پیشنهاد ویژه "
                    "برداشته شد و قیمت‌ها به حالت اصلی برگشت.",
                )

    def has_add_permission(self, request):
        return not DiscountCampaign.objects.exists()
