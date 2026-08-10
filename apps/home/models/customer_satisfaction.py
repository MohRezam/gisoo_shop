from django.db import models

from core_gisoo_backend.storage_backends.locations import customer_satisfaction_path
from django.utils.translation import gettext_lazy as _

class CustomerSatisfaction(models.Model):
    image = models.ImageField(
        upload_to=customer_satisfaction_path(), verbose_name=_("image")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("is_active"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created_at"))

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Customer Satisfaction {self.id}"
