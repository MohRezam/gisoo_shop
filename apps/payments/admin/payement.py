from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html_join

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
from django.utils.html import format_html


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


@admin.register(DestinationCard)
class DestinationCardAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "masked_pan",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "card_number",
        "display_pan",
        "masked_pan",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )
    list_per_page = 15
    list_display_links = ("name",)
    fieldsets = (
        (
            "اطلاعات کارت",
            {
                "fields": (
                    "name",
                    "card_number",
                    "display_pan",
                    "masked_pan",
                    "is_active",
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


@admin.register(PaymentIntent)
class PaymentIntentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "customer_phone",
        "payable_amount_rial",
        "status",
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
        (
            "عملیات",
            {
                "fields": (
                    "admin_action_links",
                ),
            },
        ),
    )

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
        )

    @admin.display(description="عملیات")
    def admin_actions(self, obj):
        return self._action_links(obj)

    @admin.display(description="تأیید / رد رسید")
    def admin_action_links(self, obj):
        return format_html(
            '<div style="display:flex;gap:8px;flex-wrap:wrap;">{}</div>',
            self._action_links(obj),
        )

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

        context = {
            **self.admin_site.each_context(request),
            "title": "تأیید رسید پرداخت",
            "form": form,
            "payment_intent": payment_intent,
            "opts": self.model._meta,
            "has_view_permission": self.has_view_permission(
                request,
                payment_intent,
            ),
        }

        return TemplateResponse(
            request,
            "admin/payments/paymentintent/action_form.html",
            context,
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

        context = {
            **self.admin_site.each_context(request),
            "title": "رد رسید پرداخت",
            "form": form,
            "payment_intent": payment_intent,
            "opts": self.model._meta,
            "has_view_permission": self.has_view_permission(
                request,
                payment_intent,
            ),
        }

        return TemplateResponse(
            request,
            "admin/payments/paymentintent/action_form.html",
            context,
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
