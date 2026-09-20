from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.home"
    verbose_name = "صفحه اصلی"

    def ready(self):
        from apps.home.signals import register_home_cache_signals

        register_home_cache_signals()

