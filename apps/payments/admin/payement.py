from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html, format_html_join
from django.utils.safestring import SafeString, mark_safe

from apps.payments.admin.admin_forms import PaymentRejectForm, PaymentApproveForm
from apps.payments.models import (
    DestinationCard,
    PaymentIntent,
    PaymentReceipt,
    PaymentReview,
)
from apps.payments.services.review_payment import (
    approve_payment,
    reject_payment,
)
from apps.shared.admin_filters import PersianChoicesFilter


def _form_error_message(exc):
    """Flatten DRF/Django validation errors for admin forms."""
    detail = getattr(exc, "detail", None)
    if detail is None:
        return str(exc)
    if isinstance(detail, list):
        return " ".join(str(item) for item in detail)
    if isinstance(detail, dict):
        parts = []
        for value in detail.values():
            if isinstance(value, list):
                parts.extend(str(item) for item in value)
            else:
                parts.append(str(value))
        return " ".join(parts)
    return str(detail)


def _receipt_file_url(receipt: PaymentReceipt) -> str:
    try:
        return receipt.file.url if receipt.file else ""
    except (ValueError, OSError):
        return ""


def _is_image_receipt(receipt: PaymentReceipt) -> bool:
    mime = (receipt.mime_type or "").lower()
    if mime.startswith("image/"):
        return True
    name = (receipt.original_name or getattr(receipt.file, "name", "") or "").lower()
    return name.endswith((".jpg", ".jpeg", ".png", ".webp", ".gif"))


def _active_receipts_for_intent(payment_intent) -> list[PaymentReceipt]:
    if payment_intent is None:
        return []
    cached = getattr(payment_intent, "_prefetched_objects_cache", {}).get("receipts")
    if cached is not None:
        return [r for r in cached if r.is_active]
    return list(
        payment_intent.receipts.filter(is_active=True).order_by("-uploaded_at", "-id")
    )


def render_receipt_preview_html(
    receipts: list[PaymentReceipt],
    *,
    empty_message: str = "هنوز رسیدی ارسال نشده است.",
) -> SafeString:
    """HTML preview of receipt image(s)/PDF for admin review screens."""
    if not receipts:
        return format_html(
            '<div class="gisoo-receipt-empty">{}</div>',
            empty_message,
        )

    blocks: list[str] = []
    for receipt in receipts:
        url = _receipt_file_url(receipt)
        label = receipt.original_name or f"رسید #{receipt.pk}"
        meta = format_html(
            '<div class="gisoo-receipt-meta">'
            "<span>{}</span>"
            "<span>{}</span>"
            "</div>",
            label,
            receipt.mime_type or "فایل",
        )

        if not url:
            blocks.append(
                format_html(
                    '<div class="gisoo-receipt-card">{}'
                    '<p class="gisoo-receipt-missing">فایل رسید در دسترس نیست.</p>'
                    "</div>",
                    meta,
                )
            )
            continue

        if _is_image_receipt(receipt):
            body = format_html(
                '<a class="gisoo-receipt-open" href="{}" target="_blank" rel="noopener">'
                '<img class="gisoo-receipt-img" src="{}" alt="رسید پرداخت" loading="lazy" />'
                "</a>"
                '<a class="button gisoo-receipt-link" href="{}" target="_blank" rel="noopener">'
                "باز کردن تصویر در تب جدید"
                "</a>",
                url,
                url,
                url,
            )
        else:
            body = format_html(
                '<div class="gisoo-receipt-file">'
                "<p>این رسید تصویر نیست (مثلاً PDF). برای مشاهده باز کنید.</p>"
                '<a class="button gisoo-receipt-link" href="{}" target="_blank" rel="noopener">'
                "دانلود / مشاهده فایل"
                "</a>"
                "</div>",
                url,
            )

        blocks.append(
            format_html(
                '<div class="gisoo-receipt-card">{}{}</div>',
                meta,
                body,
            )
        )

    return mark_safe(
        format_html(
            '<div class="gisoo-receipt-preview">{}</div>',
            mark_safe("".join(blocks)),
        )
    )


@admin.register(DestinationCard)
class DestinationCardAdmin(admin.ModelAdmin):
    """
    Singleton shop destination card: at most one row.
    Employer can create once, then only edit.
    """

    list_display = (
        "name",
        "masked_pan",
        "bank_name",
        "is_active",
        "updated_at",
    )

    search_fields = (
        "name",
        "card_number",
        "bank_name",
        "display_pan",
        "masked_pan",
    )

    readonly_fields = (
        "display_pan",
        "masked_pan",
        "created_at",
        "updated_at",
    )
    list_per_page = 15
    list_display_links = ("name",)
    fieldsets = (
        (
            "اطلاعات کارت فروشگاه",
            {
                "description": (
                    "فقط یک کارت مقصد در کل سایت مجاز است. "
                    "شماره کارت، نام دارنده و در صورت تمایل نام بانک را وارد کنید؛ "
                    "نمایش ماسک‌شده به‌صورت خودکار ساخته می‌شود."
                ),
                "fields": (
                    "name",
                    "card_number",
                    "bank_name",
                    "is_active",
                ),
            },
        ),
        (
            "پیش‌نمایش خودکار",
            {
                "fields": (
                    "display_pan",
                    "masked_pan",
                ),
            },
        ),
        (
            "سیستم",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    def has_add_permission(self, request):
        return not DestinationCard.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        from django.shortcuts import redirect

        obj = DestinationCard.objects.first()
        if obj is not None:
            return redirect(
                f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
                obj.pk,
            )
        return super().changelist_view(request, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        obj.full_clean()
        super().save_model(request, obj, form, change)


@admin.register(PaymentIntent)
class PaymentIntentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "customer_phone",
        "payable_amount_rial",
        "status",
        "receipt_thumb",
        "expires_at",
        "paid_at",
        "admin_actions",
    )

    list_filter = (
        ("status", PersianChoicesFilter),
    )

    search_fields = (
        "token",
        "order__id",
        "bank_reference",
    )

    readonly_fields = (
        "token",
        "status",
        "base_amount_rial",
        "unique_suffix",
        "adjustment_discount",
        "payable_amount_rial",
        "created_at",
        "updated_at",
        "paid_at",
        "reviewed_at",
        "reviewed_by",
        "receipt_preview",
        "admin_action_links",
    )

    raw_id_fields = ("order", "destination_card")
    list_per_page = 15
    list_display_links = ("order",)
    fieldsets = (
        (
            "پرداخت",
            {
                "description": "اطلاعات مبلغ و کارت مقصد برای کارت‌به‌کارت.",
                "fields": (
                    "order",
                    "destination_card",
                    "status",
                    "base_amount_rial",
                    "unique_suffix",
                    "adjustment_discount",
                    "payable_amount_rial",
                    "expires_at",
                ),
            },
        ),
        (
            "رسید مشتری",
            {
                "description": (
                    "عکس/فایل رسید همین‌جا نمایش داده می‌شود؛ "
                    "نیازی به رفتن به بخش جداگانه «رسیدهای پرداخت» نیست."
                ),
                "fields": (
                    "receipt_preview",
                ),
            },
        ),
        (
            "بررسی رسید",
            {
                "description": (
                    "رفرنس بانک = شماره پیگیری تراکنش در صورتحساب مقصد."
                ),
                "fields": (
                    "submitted_at",
                    "reviewed_at",
                    "reviewed_by",
                    "bank_reference",
                    "rejection_reason",
                    "admin_action_links",
                ),
            },
        ),
        (
            "سیستم",
            {
                "fields": (
                    "token",
                    "created_at",
                    "updated_at",
                    "paid_at",
                ),
            },
        ),
    )

    class Media:
        css = {
            "all": ("admin/css/gisoo_payment_receipt.css",),
        }

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "order",
                "order__user",
                "destination_card",
                "reviewed_by",
            )
            .prefetch_related(
                Prefetch(
                    "receipts",
                    queryset=PaymentReceipt.objects.order_by(
                        "-uploaded_at",
                        "-id",
                    ),
                )
            )
        )

    @admin.display(description="رسید")
    def receipt_thumb(self, obj):
        receipts = _active_receipts_for_intent(obj)
        if not receipts:
            return "—"
        receipt = receipts[0]
        url = _receipt_file_url(receipt)
        if not url:
            return "دارد"
        if _is_image_receipt(receipt):
            return format_html(
                '<a href="{}" target="_blank" rel="noopener" title="مشاهده رسید">'
                '<img class="gisoo-receipt-thumb" src="{}" alt="رسید" />'
                "</a>",
                url,
                url,
            )
        return format_html(
            '<a class="button" href="{}" target="_blank" rel="noopener">فایل</a>',
            url,
        )

    @admin.display(description="پیش‌نمایش رسید")
    def receipt_preview(self, obj):
        return render_receipt_preview_html(_active_receipts_for_intent(obj))

    @admin.display(description="عملیات")
    def admin_actions(self, obj):
        return self._action_links(obj)

    @admin.display(description="تأیید / رد رسید")
    def admin_action_links(self, obj):
        return format_html(
            '<div style="display:flex;gap:8px;flex-wrap:wrap;">{}</div>',
            self._action_links(obj),
        )

    def _action_context(self, request, payment_intent, *, title, form):
        return {
            **self.admin_site.each_context(request),
            "title": title,
            "form": form,
            "payment_intent": payment_intent,
            "receipts": _active_receipts_for_intent(payment_intent),
            "receipt_preview_html": render_receipt_preview_html(
                _active_receipts_for_intent(payment_intent),
                empty_message="رسید فعالی برای این پرداخت پیدا نشد.",
            ),
            "opts": self.model._meta,
            "has_view_permission": self.has_view_permission(
                request,
                payment_intent,
            ),
            "media": self.media,
        }

    def _action_links(self, obj):
        links = []

        if obj.status == "receipt_submitted":
            approve_url = reverse(
                "admin:payments_paymentintent_approve",
                args=[obj.pk],
            )

            reject_url = reverse(
                "admin:payments_paymentintent_reject",
                args=[obj.pk],
            )

            links.append(
                (approve_url, "تأیید رسید")
            )

            links.append(
                (reject_url, "رد رسید")
            )

        if not links:
            return "-"

        return format_html_join(
            " ",
            '<a class="button" href="{}">{}</a>',
            links,
        )

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "<int:payment_intent_id>/approve/",
                self.admin_site.admin_view(
                    self.approve_view
                ),
                name="payments_paymentintent_approve",
            ),
            path(
                "<int:payment_intent_id>/reject/",
                self.admin_site.admin_view(
                    self.reject_view
                ),
                name="payments_paymentintent_reject",
            ),

        ]

        return custom_urls + urls

    def approve_view(self, request, payment_intent_id):
        payment_intent = self.get_object(request, payment_intent_id)

        if payment_intent is None:
            self.message_user(
                request,
                "پرداخت یافت نشد.",
                level=messages.ERROR,
            )
            return HttpResponseRedirect(
                reverse("admin:payments_paymentintent_changelist")
            )

        if not self.has_change_permission(request, payment_intent):
            raise PermissionDenied

        if request.method == "POST":
            form = PaymentApproveForm(request.POST)

            if form.is_valid():
                try:
                    approve_payment(
                        payment_intent_id=payment_intent.pk,
                        admin=request.user,
                        bank_verified=form.cleaned_data["bank_verified"],
                        bank_reference=form.cleaned_data["bank_reference"],
                        reason=form.cleaned_data.get("reason", ""),
                    )

                except Exception as exc:
                    form.add_error(
                        None,
                        _form_error_message(exc),
                    )
                else:
                    self.message_user(
                        request,
                        "رسید با موفقیت تأیید شد.",
                        level=messages.SUCCESS,
                    )

                    return HttpResponseRedirect(
                        reverse(
                            "admin:payments_paymentintent_change",
                            args=[payment_intent.pk],
                        )
                    )
        else:
            form = PaymentApproveForm()

        return TemplateResponse(
            request,
            "admin/payments/paymentintent/action_form.html",
            self._action_context(
                request,
                payment_intent,
                title="تأیید رسید پرداخت",
                form=form,
            ),
        )

    def reject_view(self, request, payment_intent_id):
        payment_intent = self.get_object(request, payment_intent_id)

        if payment_intent is None:
            self.message_user(
                request,
                "پرداخت یافت نشد.",
                level=messages.ERROR,
            )
            return HttpResponseRedirect(
                reverse("admin:payments_paymentintent_changelist")
            )

        if not self.has_change_permission(request, payment_intent):
            raise PermissionDenied

        if request.method == "POST":
            form = PaymentRejectForm(request.POST)

            if form.is_valid():
                try:
                    reject_payment(
                        payment_intent_id=payment_intent.pk,
                        admin=request.user,
                        reason=form.cleaned_data["reason"],
                    )

                except Exception as exc:
                    form.add_error(
                        None,
                        _form_error_message(exc),
                    )
                else:
                    self.message_user(
                        request,
                        "رسید رد شد.",
                        level=messages.SUCCESS,
                    )

                    return HttpResponseRedirect(
                        reverse(
                            "admin:payments_paymentintent_change",
                            args=[payment_intent.pk],
                        )
                    )
        else:
            form = PaymentRejectForm()

        return TemplateResponse(
            request,
            "admin/payments/paymentintent/action_form.html",
            self._action_context(
                request,
                payment_intent,
                title="رد رسید پرداخت",
                form=form,
            ),
        )

    @admin.display(description="Phone", ordering="order__user__phone")
    def customer_phone(self, obj):
        if not obj.order or not obj.order.user:
            return "-"

        return obj.order.user.phone_number or "-"


@admin.register(PaymentReceipt)
class PaymentReceiptAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "payment_intent",
        "receipt_thumb",
        "original_name",
        "mime_type",
        "file_size",
        "is_active",
        "uploaded_at",
    )

    list_filter = (
        "is_active",
        "mime_type",
    )

    search_fields = (
        "sha256",
        "original_name",
        "idempotency_key",
    )

    readonly_fields = (
        "receipt_preview",
        "sha256",
        "idempotency_key",
        "created_at",
        "updated_at",
        "uploaded_at",
    )
    list_per_page = 15
    exclude = ("creator", "archived")
    raw_id_fields = ("payment_intent",)
    list_display_links = ("payment_intent",)
    fieldsets = (
        (
            "رسید",
            {
                "fields": (
                    "payment_intent",
                    "receipt_preview",
                    "file",
                    "original_name",
                    "mime_type",
                    "file_size",
                    "is_active",
                ),
            },
        ),
        (
            "سیستم",
            {
                "fields": (
                    "sha256",
                    "idempotency_key",
                    "uploaded_at",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    class Media:
        css = {
            "all": ("admin/css/gisoo_payment_receipt.css",),
        }

    @admin.display(description="پیش‌نمایش")
    def receipt_thumb(self, obj):
        url = _receipt_file_url(obj)
        if not url:
            return "—"
        if _is_image_receipt(obj):
            return format_html(
                '<a href="{}" target="_blank" rel="noopener">'
                '<img class="gisoo-receipt-thumb" src="{}" alt="رسید" />'
                "</a>",
                url,
                url,
            )
        return format_html(
            '<a class="button" href="{}" target="_blank" rel="noopener">فایل</a>',
            url,
        )

    @admin.display(description="پیش‌نمایش رسید")
    def receipt_preview(self, obj):
        if not obj or not obj.pk:
            return "—"
        return render_receipt_preview_html([obj])


@admin.register(PaymentReview)
class PaymentReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "payment_intent",
        "admin",
        "decision",
        "bank_reference",
        "bank_verified",
        "created_at",
    )

    list_filter = (
        "decision",
        "bank_verified",
    )

    search_fields = (
        "bank_reference",
        "reason",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )
    raw_id_fields = ("payment_intent", "admin")
    list_per_page = 15
    list_display_links = ("payment_intent",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        # Superuser must be able to delete so PaymentIntent cascade
        # delete is not blocked by related PaymentReview rows.
        return bool(request.user and request.user.is_superuser)
