# Application definition
LOCAL_APPS = [
    "apps.users",
    "apps.addresses",
    "apps.cart",
    "apps.discounts",
    "apps.notifications",
    "apps.orders",
    "apps.payments",
    "apps.products",
    "apps.shipping",
    "apps.home"
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework.authtoken",
    "django_extensions",
    "debug_toolbar",
    "storages",
    "corsheaders",
    "django_prometheus",
    "multiselectfield",
    "django_admin_inline_paginator",
    "fcm_django",
    "simple_history",
    "health_check",
    # "health_check.db",
    # "health_check.storage",
    "admin_auto_filters",
    "drf_spectacular",
    "django_object_actions",
    # "jalali_date",
    "import_export",
    "silk",
    "rest_framework_simplejwt.token_blacklist",
    "colorfield",
    "django_cleanup",
    "django_celery_beat",
]

DEFAULT_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

LATE_LOAD_THIRD_PARTY_APPS = []

INSTALLED_APPS = (
    DEFAULT_APPS + THIRD_PARTY_APPS + LOCAL_APPS + LATE_LOAD_THIRD_PARTY_APPS
)
