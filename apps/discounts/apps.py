from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DiscountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.discounts"
    verbose_name = _("Discounts App")

