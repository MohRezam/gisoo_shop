from django.db import models
from django.utils.translation import gettext_lazy as _


class Permission(models.Model):
    title = models.CharField(max_length=128, verbose_name=_("title"))
    description = models.TextField(null=True, blank=True, verbose_name=_("description"))

    class Meta:
        verbose_name = _("Permission")
        verbose_name_plural = _("Permissions")
