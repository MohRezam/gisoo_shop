from django.db import models
from django.utils.translation import gettext_lazy as _

class FAQCategory(models.Model):
    title = models.CharField(
        max_length=100,
        verbose_name=_("title"),
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        verbose_name=_("slug"),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("is_active"),
    )
    ordering = models.PositiveIntegerField(
        default=0,
        verbose_name=_("ordering"),
    )

    class Meta:
        verbose_name = _("FAQCategory")
        verbose_name_plural = _("FAQCategories")
        ordering = ["ordering", "id"]

    def __str__(self):
        return self.title


class FAQ(models.Model):
    category = models.ForeignKey(
        FAQCategory,
        on_delete=models.CASCADE,
        related_name="faqs",
        verbose_name=_("category"),
    )
    question = models.CharField(
        max_length=500,
        verbose_name=_("question"),
    )
    answer = models.TextField(
        verbose_name=_("answer"),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("is_active"),
    )
    ordering = models.PositiveIntegerField(
        default=0,
        verbose_name=_("ordering"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("created_at")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("updated_at")
    )

    class Meta:
        verbose_name = _("FAQ")
        verbose_name_plural = _("FAQs")
        ordering = ["ordering", "id"]

    def __str__(self):
        return self.question