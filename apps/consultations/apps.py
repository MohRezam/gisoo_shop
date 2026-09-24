from django.apps import AppConfig


class ConsultationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.consultations"
    verbose_name = "مشاوره‌ها"

    def ready(self):
        from apps.consultations.signals import register_consultation_cache_signals

        register_consultation_cache_signals()
