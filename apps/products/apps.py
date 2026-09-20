from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ProductsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.products"
    verbose_name = "محصولات"

    def ready(self):
        from apps.products.signals import stock_notify  # noqa: F401
        from apps.products.signals.cache_invalidation import (
            register_product_cache_signals,
        )

        register_product_cache_signals()

