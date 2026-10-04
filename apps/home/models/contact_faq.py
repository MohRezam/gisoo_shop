from django.core.exceptions import ValidationError
from django.db import models

MAX_CONTACT_FAQS = 6


class ContactFAQ(models.Model):
    """سوالات متداول اختصاصی صفحه تماس با ما (/contact)."""

    question = models.CharField(
        max_length=500,
        verbose_name="سوال",
    )
    answer = models.TextField(
        verbose_name="پاسخ",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )
    ordering = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ به‌روزرسانی",
    )

    class Meta:
        verbose_name = "سوال متداول تماس"
        verbose_name_plural = "سوالات متداول تماس"
        ordering = ["ordering", "id"]

    def __str__(self):
        return self.question

    def clean(self):
        super().clean()
        qs = ContactFAQ.objects.all()
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.count() >= MAX_CONTACT_FAQS:
            raise ValidationError(
                f"حداکثر {MAX_CONTACT_FAQS} سوال برای صفحه تماس مجاز است.",
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
