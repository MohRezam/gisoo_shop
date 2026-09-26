"""
Sync Celery beat_schedule from code into django-celery-beat PeriodicTask rows.

Required when CELERY_BEAT_SCHEDULER=DatabaseScheduler (production default):
the in-code beat_schedule is NOT auto-imported.

Usage:
  python manage.py sync_celery_beat
"""

from datetime import timedelta

from celery.schedules import crontab, schedule as celery_schedule
from django.core.management.base import BaseCommand
from django_celery_beat.models import (
    CrontabSchedule,
    IntervalSchedule,
    PeriodicTask,
)


class Command(BaseCommand):
    help = "ثبت/به‌روزرسانی وظایف دوره‌ای Celery از beat_schedule کد"

    def handle(self, *args, **options):
        from core_gisoo_backend.celery import app

        beat_schedule = app.conf.beat_schedule or {}
        if not beat_schedule:
            self.stdout.write(self.style.WARNING("beat_schedule خالی است."))
            return

        created = 0
        updated = 0

        for name, entry in beat_schedule.items():
            task = entry["task"]
            sched = entry["schedule"]
            defaults = {
                "task": task,
                "enabled": True,
            }

            if isinstance(sched, crontab):
                cron, _ = CrontabSchedule.objects.get_or_create(
                    minute=sched._orig_minute,
                    hour=sched._orig_hour,
                    day_of_week=sched._orig_day_of_week,
                    day_of_month=sched._orig_day_of_month,
                    month_of_year=sched._orig_month_of_year,
                    timezone=str(getattr(sched, "tz", None) or "UTC"),
                )
                defaults["crontab"] = cron
                defaults["interval"] = None
            else:
                # float seconds or celery schedule object
                if isinstance(sched, (int, float)):
                    every = int(sched)
                elif isinstance(sched, celery_schedule):
                    every = int(sched.run_every.total_seconds())
                elif isinstance(sched, timedelta):
                    every = int(sched.total_seconds())
                else:
                    every = int(float(sched))

                interval, _ = IntervalSchedule.objects.get_or_create(
                    every=max(every, 1),
                    period=IntervalSchedule.SECONDS,
                )
                defaults["interval"] = interval
                defaults["crontab"] = None

            obj, was_created = PeriodicTask.objects.update_or_create(
                name=name,
                defaults=defaults,
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"+ {name} → {task}"))
            else:
                updated += 1
                self.stdout.write(f"~ {name} → {task}")

        self.stdout.write(
            self.style.SUCCESS(
                f"تمام. ایجاد={created} به‌روزرسانی={updated}. "
                "celery-beat را یک‌بار ری‌استارت کنید."
            )
        )
