from django.contrib import admin, messages
from django.http import HttpResponseRedirect

from apps.home.models import ContactFAQ, MAX_CONTACT_FAQS


@admin.register(ContactFAQ)
class ContactFAQAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "question",
        "is_active",
        "ordering",
        "updated_at",
    )
    list_filter = ("is_active",)
    search_fields = (
        "question",
        "answer",
    )
    list_editable = (
        "is_active",
        "ordering",
    )
    ordering = (
        "ordering",
        "id",
    )
    list_per_page = 15
    list_display_links = ("question",)

    def has_add_permission(self, request):
        if ContactFAQ.objects.count() >= MAX_CONTACT_FAQS:
            return False
        return super().has_add_permission(request)

    def changelist_view(self, request, extra_context=None):
        count = ContactFAQ.objects.count()
        if count >= MAX_CONTACT_FAQS:
            messages.info(
                request,
                f"حداکثر {MAX_CONTACT_FAQS} سوال برای صفحه تماس مجاز است "
                f"({count} مورد ثبت شده).",
            )
        return super().changelist_view(request, extra_context=extra_context)

    def add_view(self, request, form_url="", extra_context=None):
        if ContactFAQ.objects.count() >= MAX_CONTACT_FAQS:
            messages.error(
                request,
                f"حداکثر {MAX_CONTACT_FAQS} سوال برای صفحه تماس مجاز است.",
            )
            return HttpResponseRedirect("../")
        return super().add_view(request, form_url, extra_context)
