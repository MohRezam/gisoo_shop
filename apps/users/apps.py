from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"
    verbose_name = "کاربران"

    def ready(self):
        from apps.users.models import User

        field_labels = {
            "password": "رمز عبور",
            "last_login": "آخرین ورود",
            "is_superuser": "مدیر کل",
            "groups": "گروه‌ها",
            "user_permissions": "مجوزهای کاربر",
        }
        for name, label in field_labels.items():
            try:
                User._meta.get_field(name).verbose_name = label
            except Exception:
                pass
