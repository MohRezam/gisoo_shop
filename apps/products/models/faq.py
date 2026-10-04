from django.core.exceptions import ValidationError
from django.db import models

MAX_PRODUCT_FAQS = 6


class ProductFAQ(models.Model):
    """سوالات متداول اختصاصی هر محصول (حداکثر ۶ مورد)."""

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="faqs",
        verbose_name="محصول",
    )
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
        verbose_name = "سوال متداول محصول"
        verbose_name_plural = "سوالات متداول محصول"
        ordering = ["ordering", "id"]

    def __str__(self):
        return self.question

    def clean(self):
        super().clean()
        if not self.product_id:
            return
        qs = ProductFAQ.objects.filter(product_id=self.product_id)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.count() >= MAX_PRODUCT_FAQS:
            raise ValidationError(
                f"حداکثر {MAX_PRODUCT_FAQS} سوال برای هر محصول مجاز است.",
            )
