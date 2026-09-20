from django.apps import AppConfig


class SharedConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.shared"
    verbose_name = "اشتراکی"

    def ready(self):
        from django.apps import apps

        renames = {
            "auth": "احراز هویت و مجوزها",
            "authtoken": "توکن‌های ورود",
            "token_blacklist": "لیست سیاه توکن",
            "sessions": "نشست‌ها",
            "admin": "مدیریت سایت",
            "contenttypes": "انواع محتوا",
            "sites": "سایت‌ها",
            "fcm_django": "دستگاه‌های اعلان پوش",
            "django_celery_beat": "زمان‌بندی سلری",
            "silk": "پروفایلر سیلک",
        }
        for label, title in renames.items():
            try:
                apps.get_app_config(label).verbose_name = title
            except LookupError:
                pass

        try:
            FCMDevice = apps.get_model("fcm_django", "FCMDevice")
            FCMDevice._meta.verbose_name = "دستگاه اعلان"
            FCMDevice._meta.verbose_name_plural = "دستگاه‌های اعلان"
        except LookupError:
            pass

        try:
            from django.contrib.auth.models import Group

            Group._meta.verbose_name = "گروه"
            Group._meta.verbose_name_plural = "گروه‌ها"
        except Exception:
            pass

        try:
            Token = apps.get_model("authtoken", "Token")
            Token._meta.verbose_name = "توکن"
            Token._meta.verbose_name_plural = "توکن‌ها"
        except LookupError:
            pass
