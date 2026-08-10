from django.db import models

from core_gisoo_backend.storage_backends.locations import customer_satisfaction_path


class CustomerSatisfaction(models.Model):
    image = models.ImageField(
        upload_to=customer_satisfaction_path()
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Customer Satisfaction {self.id}"
