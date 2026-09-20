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

        celery_renames = {
            "ClockedSchedule": ("زمان‌بندی ساعتی", "زمان‌بندی‌های ساعتی"),
            "CrontabSchedule": ("زمان‌بندی کرontab", "زمان‌بندی‌های کرontab"),
            "IntervalSchedule": ("بازه زمانی", "بازه‌های زمانی"),
            "PeriodicTask": ("وظیفه دوره‌ای", "وظایف دوره‌ای"),
            "PeriodicTasks": ("ردیابی وظیفه دوره‌ای", "ردیابی وظایف دوره‌ای"),
            "SolarSchedule": ("رویداد خورشیدی", "رویدادهای خورشیدی"),
        }
        for model_name, (singular, plural) in celery_renames.items():
            try:
                model = apps.get_model("django_celery_beat", model_name)
                model._meta.verbose_name = singular
                model._meta.verbose_name_plural = plural
            except LookupError:
                pass

        blacklist_renames = {
            "BlacklistedToken": ("توکن مسدودشده", "توکن‌های مسدودشده"),
            "OutstandingToken": ("توکن فعال", "توکن‌های فعال"),
        }
        for model_name, (singular, plural) in blacklist_renames.items():
            try:
                model = apps.get_model("token_blacklist", model_name)
                model._meta.verbose_name = singular
                model._meta.verbose_name_plural = plural
            except LookupError:
                pass
