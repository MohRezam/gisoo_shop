from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.payments"
    verbose_name = "پرداخت‌ها"

    def ready(self):
        from apps.payments.signals import register_payments_cache_signals

        register_payments_cache_signals()
