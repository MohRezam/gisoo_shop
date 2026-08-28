from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserPhoneNumber(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="phone_numbers",
        verbose_name=_("user"),
    )

    phone_number = models.CharField(
        _("phone number"),
        max_length=15,
    )

    is_verified = models.BooleanField(
        _("is verified"),
        default=False,
    )

    is_primary = models.BooleanField(
        _("is primary"),
        default=False,
    )

    created_at = models.DateTimeField(
        _("created at"),
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        _("updated at"),
        auto_now=True,
    )

    class Meta:
        verbose_name = _("user phone number")
        verbose_name_plural = _("user phone numbers")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "phone_number"],
                name="unique_user_phone_number",
            ),
        ]
        ordering = ["-is_primary", "-created_at"]

    def __str__(self):
        return self.phone_number