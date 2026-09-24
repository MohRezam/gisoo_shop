from django.contrib import admin, messages
from django.http import HttpResponseRedirect

from apps.consultations.models import ConsultationFAQ, MAX_CONSULTATION_FAQS


@admin.register(ConsultationFAQ)
class ConsultationFAQAdmin(admin.ModelAdmin):
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
        if ConsultationFAQ.objects.count() >= MAX_CONSULTATION_FAQS:
            return False
        return super().has_add_permission(request)

    def changelist_view(self, request, extra_context=None):
        count = ConsultationFAQ.objects.count()
        if count >= MAX_CONSULTATION_FAQS:
            messages.info(
                request,
                f"حداکثر {MAX_CONSULTATION_FAQS} سوال برای صفحه مشاوره مجاز است "
                f"({count} مورد ثبت شده).",
            )
        return super().changelist_view(request, extra_context=extra_context)

    def add_view(self, request, form_url="", extra_context=None):
        if ConsultationFAQ.objects.count() >= MAX_CONSULTATION_FAQS:
            messages.error(
                request,
                f"حداکثر {MAX_CONSULTATION_FAQS} سوال برای صفحه مشاوره مجاز است.",
            )
            return HttpResponseRedirect("../")
        return super().add_view(request, form_url, extra_context)
