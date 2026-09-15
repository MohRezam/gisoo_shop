# core_gisoo_backend/celery.py

from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "core_gisoo_backend.settings",
)

app = Celery("core_gisoo_backend")

app.config_from_object(
    "django.conf:settings",
    namespace="CELERY",
)

app.autodiscover_tasks(
    lambda: settings.INSTALLED_APPS,
)

app.conf.beat_schedule = {
    "expire-overdue-orders-every-minute": {
        "task": "apps.orders.tasks.expire_overdue_orders",
        "schedule": 60.0,
    },
}