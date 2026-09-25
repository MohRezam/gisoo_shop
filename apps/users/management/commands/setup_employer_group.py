"""
Create / refresh the employer staff group with safe shop permissions.

Usage:
  python manage.py setup_employer_group
"""

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

GROUP_NAME = "فروشگاه-کارفرما"

# App labels / model names the employer may use (view/add/change).
# Delete is intentionally limited — see EXCLUDE_DELETE.
ALLOW_MODELS = {
    "orders": {"order", "orderitem", "orderbundle"},
    "payments": {
        "paymentintent",
        "paymentreceipt",
        "paymentreview",
        "destinationcard",
        "paymentguidevideo",
    },
    "products": {
        "product",
        "productvariant",
        "productimage",
        "productfaq",
        "category",
        "brand",
        "bundle",
        "discountcampaign",
        "hairproblem",
        "hairtype",
        "attribute",
        "attributevalue",
    },
    "home": {
        "banner",
        "slider",
        "homeabout",
        "faq",
        "faqcategory",
        "contactfaq",
        "sociallinks",
        "customersatisfaction",
    },
    "discounts": {"discountcode", "discountusage"},
    "reviews": {"productreview"},
    "consultations": {
        "consultationrequest",
        "consultationrecommendation",
        "consultationpack",
        "consultationfaq",
    },
    "magazine": {"magazinepost", "magazinecategory"},
    "shipping": {"shippingmethod", "shippingcarrier"},
    "notifications": {"adminalert", "inappnotification", "smssettings"},
    "marketing": {"newslettersubscriber"},
    "addresses": {"address"},
}

# Never grant these to the employer group.
DENY_APPS = {"auth", "admin", "contenttypes", "sessions", "silk", "django_celery_beat"}


class Command(BaseCommand):
    help = "ایجاد گروه دسترسی فروشگاه-کارفرما برای کار با پنل بدون سوپریوزر"

    def handle(self, *args, **options):
        group, _ = Group.objects.get_or_create(name=GROUP_NAME)
        perms = []

        for app_label, models in ALLOW_MODELS.items():
            for model in models:
                ct = ContentType.objects.filter(
                    app_label=app_label,
                    model=model,
                ).first()
                if ct is None:
                    continue
                for codename_prefix in ("view", "add", "change"):
                    codename = f"{codename_prefix}_{model}"
                    perm = Permission.objects.filter(
                        content_type=ct,
                        codename=codename,
                    ).first()
                    if perm:
                        perms.append(perm)
                # Limited delete only for soft content (reviews / alerts)
                if model in {"productreview", "adminalert", "inappnotification"}:
                    perm = Permission.objects.filter(
                        content_type=ct,
                        codename=f"delete_{model}",
                    ).first()
                    if perm:
                        perms.append(perm)

        group.permissions.set(perms)
        self.stdout.write(
            self.style.SUCCESS(
                f"گروه «{GROUP_NAME}» با {len(perms)} دسترسی آماده شد. "
                "کاربر کارفرما را staff کنید و این گروه را به او بدهید؛ "
                "is_superuser ندهید."
            )
        )
        self.stdout.write(
            "باز: سفارش، رسید، محصول، محتوا، نظرات، مشاوره، آمار.\n"
            "بسته: کاربران/گروه‌ها/پرمیشن خام، لاگ نوتیف SMS، celery، silk."
        )
