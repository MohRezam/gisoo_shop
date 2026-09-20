# Application definition
from core_gisoo_backend import settings
from core_gisoo_backend.settings.components.common import DEBUG

LOCAL_APPS = [
    "apps.users.apps.UsersConfig",
    "apps.addresses.apps.AddressesConfig",
    "apps.cart.apps.CartConfig",
    "apps.discounts.apps.DiscountsConfig",
    "apps.notifications.apps.NotificationsConfig",
    "apps.orders.apps.OrdersConfig",
    "apps.payments.apps.PaymentsConfig",
    "apps.products.apps.ProductsConfig",
    "apps.shipping.apps.ShippingConfig",
    "apps.home.apps.HomeConfig",
    "apps.magazine.apps.MagazineConfig",
    "apps.marketing.apps.MarketingConfig",
    "apps.consultations.apps.ConsultationsConfig",
    "apps.reviews.apps.ReviewsConfig",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework.authtoken",
    "django_extensions",
    # "debug_toolbar",
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
    "nested_admin"
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

if DEBUG:
    THIRD_PARTY_APPS.insert(0, "debug_toolbar")
    # THIRD_PARTY_APPS.insert(0, "silk")

INSTALLED_APPS = (
        DEFAULT_APPS + THIRD_PARTY_APPS + LOCAL_APPS + LATE_LOAD_THIRD_PARTY_APPS
)
