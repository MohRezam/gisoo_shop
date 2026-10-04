from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shared.models.base import SingletonModel


class SocialLinks(SingletonModel):
    """
    Site-wide social / messaging links (singleton).
    Edited in admin; exposed via public API for footer & contact.
    """

    telegram_url = models.URLField(
        max_length=500,
        blank=True,
        default="",
        verbose_name=_("telegram url"),
    )
    instagram_url = models.URLField(
        max_length=500,
        blank=True,
        default="",
        verbose_name=_("instagram url"),
    )
    whatsapp_url = models.URLField(
        max_length=500,
        blank=True,
        default="",
        verbose_name=_("whatsapp url"),
    )
    bale_url = models.URLField(
        max_length=500,
        blank=True,
        default="",
        verbose_name=_("bale url"),
    )

    class Meta:
        verbose_name = "لینک‌های شبکه‌های اجتماعی"
        verbose_name_plural = "لینک‌های شبکه‌های اجتماعی"

    def __str__(self):
        return "لینک‌های شبکه‌های اجتماعی"
