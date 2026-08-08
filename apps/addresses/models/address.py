from django.db import models
from django.utils.translation import gettext_lazy as _

from django.core.exceptions import ValidationError
from django.db.models import Q

from apps.shared.models.base import BaseModel


class Address(BaseModel):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="addresses",
        verbose_name=_("user"),
    )

    title = models.CharField(
        max_length=100,
        verbose_name=_("title"),
        help_text=_(
            "For example: home, work, parents"
        ),
    )

    receiver_name = models.CharField(
        max_length=255,
        verbose_name=_("receiver name"),
    )

    phone_number = models.CharField(
        max_length=11,
        verbose_name=_("phone number"),
    )

    province = models.CharField(
        max_length=100,
        verbose_name=_("province"),
    )

    city = models.CharField(
        max_length=100,
        verbose_name=_("city"),
    )

    postal_code = models.CharField(
        max_length=20,
        verbose_name=_("postal code"),
    )

    address = models.TextField(
        verbose_name=_("address"),
    )

    is_default = models.BooleanField(
        default=False,
        verbose_name=_("is default"),
    )

    class Meta:
        verbose_name = _("address")
        verbose_name_plural = _("addresses")
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(
                    is_default=True
                ),
                name="unique_default_address_per_user",
            )
        ]

    def __str__(self):
        return (
            f"{self.user.phone_number} - "
            f"{self.title}"
        )

    def clean(self):
        if self.is_default:
            exists = Address.objects.filter(
                user=self.user,
                is_default=True,
            ).exclude(
                pk=self.pk,
            ).exists()

            if exists:
                raise ValidationError(
                    _("User already has a default address.")
                )
