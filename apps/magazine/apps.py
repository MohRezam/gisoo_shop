from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MagazineConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.magazine"
    verbose_name = "مجله"

    def ready(self):
        from apps.magazine.signals import register_magazine_cache_signals

        register_magazine_cache_signals()

