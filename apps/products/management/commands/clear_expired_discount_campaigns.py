"""
Clear discounted_price on special-offer products when the campaign has ended.

Safe to run repeatedly (idempotent). Used from entrypoint on deploy and by ops.
"""

from django.core.management.base import BaseCommand

from apps.products.tasks import sweep_expired_discount_campaigns


class Command(BaseCommand):
    help = (
        "پایان کمپین‌های منقضی: برداشتن قیمت تخفیف‌خورده "
        "و غیرفعال‌کردن کمپین"
    )

    def handle(self, *args, **options):
        ended = sweep_expired_discount_campaigns()
        self.stdout.write(
            self.style.SUCCESS(
                f"کمپین‌های پایان‌یافته پاک‌سازی شد: {ended}"
            )
        )
