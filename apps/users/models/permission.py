from django.db import models


class Permission(models.Model):
    title = models.CharField(max_length=128, verbose_name="عنوان")
    description = models.TextField(null=True, blank=True, verbose_name="توضیحات")

    class Meta:
        verbose_name = "مجوز"
        verbose_name_plural = "مجوزها"
