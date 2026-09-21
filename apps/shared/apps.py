from django.apps import AppConfig


def _patch_field_labels(model, labels: dict[str, str]) -> None:
    for field_name, label in labels.items():
        try:
            field = model._meta.get_field(field_name)
        except Exception:
            continue
        field.verbose_name = label


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

        # --- Auth tokens (DRF) ---
        for model_name in ("Token", "TokenProxy"):
            try:
                model = apps.get_model("authtoken", model_name)
                model._meta.verbose_name = "توکن"
                model._meta.verbose_name_plural = "توکن‌ها"
                _patch_field_labels(
                    model,
                    {
                        "key": "کلید",
                        "user": "کاربر",
                        "created": "تاریخ ایجاد",
                    },
                )
            except LookupError:
                pass

        # --- JWT blacklist ---
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

        try:
            OutstandingToken = apps.get_model("token_blacklist", "OutstandingToken")
            _patch_field_labels(
                OutstandingToken,
                {
                    "user": "کاربر",
                    "jti": "شناسه توکن (JTI)",
                    "token": "توکن",
                    "created_at": "تاریخ ایجاد",
                    "expires_at": "تاریخ انقضا",
                },
            )
        except LookupError:
            pass

        try:
            BlacklistedToken = apps.get_model("token_blacklist", "BlacklistedToken")
            _patch_field_labels(
                BlacklistedToken,
                {
                    "token": "توکن",
                    "blacklisted_at": "زمان مسدودسازی",
                },
            )
        except LookupError:
            pass

        # --- Celery Beat ---
        celery_renames = {
            "ClockedSchedule": ("زمان‌بندی یک‌باره", "زمان‌بندی‌های یک‌باره"),
            "CrontabSchedule": ("جدول کرون", "جداول کرون"),
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

        celery_field_labels = {
            "CrontabSchedule": {
                "minute": "دقیقه",
                "hour": "ساعت",
                "day_of_month": "روز ماه",
                "month_of_year": "ماه سال",
                "day_of_week": "روز هفته",
                "timezone": "منطقه زمانی",
            },
            "IntervalSchedule": {
                "every": "تعداد دوره",
                "period": "واحد دوره",
            },
            "ClockedSchedule": {
                "clocked_time": "زمان اجرا",
            },
            "SolarSchedule": {
                "event": "رویداد خورشیدی",
                "latitude": "عرض جغرافیایی",
                "longitude": "طول جغرافیایی",
            },
            "PeriodicTask": {
                "name": "نام",
                "task": "نام تسک",
                "interval": "بازه زمانی",
                "crontab": "جدول کرون",
                "solar": "رویداد خورشیدی",
                "clocked": "زمان‌بندی یک‌باره",
                "args": "آرگومان‌های موقعیتی",
                "kwargs": "آرگومان‌های کلیدواژه‌ای",
                "queue": "صف",
                "exchange": "اکسچنج",
                "routing_key": "کلید مسیریابی",
                "headers": "هدرهای AMQP",
                "priority": "اولویت",
                "expires": "انقضا (تاریخ)",
                "expire_seconds": "انقضا (ثانیه)",
                "one_off": "اجرای یک‌باره",
                "start_time": "زمان شروع",
                "enabled": "فعال",
                "last_run_at": "آخرین اجرا",
                "total_run_count": "تعداد اجرا",
                "date_changed": "آخرین تغییر",
                "description": "توضیحات",
            },
            "PeriodicTasks": {
                "ident": "شناسه",
                "last_update": "آخرین به‌روزرسانی",
            },
        }
        for model_name, labels in celery_field_labels.items():
            try:
                model = apps.get_model("django_celery_beat", model_name)
                _patch_field_labels(model, labels)
            except LookupError:
                pass
