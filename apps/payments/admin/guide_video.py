from django.contrib import admin
from django.shortcuts import redirect
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from apps.payments.models import PaymentGuideVideo


@admin.register(PaymentGuideVideo)
class PaymentGuideVideoAdmin(admin.ModelAdmin):
    change_form_template = "admin/payments/paymentguidevideo/change_form.html"

    list_display = (
        "title",
        "source_summary",
        "is_active",
    )

    list_display_links = ("title",)

    readonly_fields = ("preview_box",)

    fieldsets = (
        (
            "نمایش در فروشگاه",
            {
                "fields": ("title", "is_active", "preview_box"),
                "description": mark_safe(
                    '<div class="gisoo-guide-lead">'
                    "این ویدیو در صفحه کارت‌به‌کارت، داخل دکمه "
                    "<strong>«آموزش پرداخت آسان»</strong> نمایش داده می‌شود."
                    "</div>"
                ),
            },
        ),
        (
            "منبع ویدیو",
            {
                "fields": ("video", "external_url"),
                "description": mark_safe(
                    '<ul class="gisoo-guide-tips">'
                    "<li>اولویت با <strong>فایل آپلودشده</strong> است؛ اگر فایل بگذارید، لینک خارجی نادیده گرفته می‌شود.</li>"
                    "<li>لینک آپارات معمولی: <code>aparat.com/v/...</code></li>"
                    "<li>لینک آپارات Shorts: <code>aparat.com/shorts/...</code></li>"
                    "<li>یوتیوب و فایل مستقیم mp4 هم پشتیبانی می‌شود.</li>"
                    "</ul>"
                ),
            },
        ),
        (
            "تصویر کاور",
            {
                "fields": ("poster",),
                "description": "اختیاری. قبل از پخش ویدیو به‌عنوان پیش‌نمایش نشان داده می‌شود.",
            },
        ),
    )

    @admin.display(description="وضعیت منبع")
    def source_summary(self, obj: PaymentGuideVideo):
        if obj.video:
            return "فایل آپلودشده"
        if (obj.external_url or "").strip():
            return "لینک خارجی"
        return "تعیین نشده"

    @admin.display(description="پیش‌نمایش فعلی")
    def preview_box(self, obj: PaymentGuideVideo):
        if not obj or not obj.pk:
            return "—"
        url = (obj.resolved_video_url or "").strip()
        poster = ""
        try:
            if obj.poster:
                poster = obj.poster.url
        except ValueError:
            poster = ""

        if not url and not poster:
            return format_html(
                '<div class="gisoo-guide-preview gisoo-guide-preview--empty">'
                "<p>هنوز ویدیویی تنظیم نشده است.</p>"
                "<span>فایل آپلود کنید یا لینک خارجی بگذارید.</span>"
                "</div>"
            )

        poster_html = ""
        if poster:
            poster_html = format_html(
                '<img class="gisoo-guide-poster" src="{}" alt="کاور ویدیو" />',
                poster,
            )

        source_label = "فایل آپلودشده" if obj.video else "لینک خارجی"
        link_html = ""
        if url:
            link_html = format_html(
                '<a class="gisoo-guide-link" href="{}" target="_blank" rel="noopener">باز کردن منبع</a>'
                '<code class="gisoo-guide-url" dir="ltr">{}</code>',
                url,
                url,
            )

        status = "فعال" if obj.is_active else "غیرفعال"
        status_class = "on" if obj.is_active else "off"

        return format_html(
            '<div class="gisoo-guide-preview">'
            '<div class="gisoo-guide-preview-media">{}</div>'
            '<div class="gisoo-guide-preview-meta">'
            '<span class="gisoo-guide-pill gisoo-guide-pill--{}">{}</span>'
            '<span class="gisoo-guide-pill">{}</span>'
            "{}"
            "</div>"
            "</div>",
            poster_html or mark_safe('<div class="gisoo-guide-poster-fallback">بدون کاور</div>'),
            status_class,
            status,
            source_label,
            link_html,
        )

    def has_add_permission(self, request):
        return not PaymentGuideVideo.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = PaymentGuideVideo.objects.first()
        if obj is not None:
            return redirect(
                f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
                obj.pk,
            )
        return super().changelist_view(request, extra_context=extra_context)
