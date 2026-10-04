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
    "send-pending-payment-reminders-every-minute": {
        "task": "apps.orders.tasks.send_pending_payment_reminders",
        "schedule": 60.0,
    },
    "process-shipped-delivery-followups-hourly": {
        "task": "apps.orders.tasks.process_shipped_delivery_followups",
        "schedule": 60.0 * 60,
    },
    "sweep-expired-discount-campaigns-every-minute": {
        "task": "apps.products.tasks.sweep_expired_discount_campaigns",
        "schedule": 60.0,
    },
    "purge-old-read-notifications-daily": {
        "task": "apps.notifications.tasks.purge_old_read_in_app_notifications",
        "schedule": crontab(hour=3, minute=30),
    },
    "purge-old-read-admin-alerts-daily": {
        "task": "apps.notifications.tasks.purge_old_read_admin_alerts",
        "schedule": crontab(hour=3, minute=40),
    },
}