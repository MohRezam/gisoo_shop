from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shared.models.base import BaseModel


class MarketingSubscriber(BaseModel):
    phone_number = models.CharField(
        max_length=11,
        unique=True,
        verbose_name=_("phone number"),
    )

    is_subscribed = models.BooleanField(
        default=True,
        verbose_name=_("is subscribed"),
    )

    subscribed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("subscribed at"),
    )

    unsubscribed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("unsubscribed at"),
    )

    class Meta:
        verbose_name = _("marketing subscriber")
        verbose_name_plural = _("marketing subscribers")
        ordering = ["-subscribed_at"]

    def __str__(self):
        return self.phone_number