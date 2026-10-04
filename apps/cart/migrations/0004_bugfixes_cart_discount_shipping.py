# Generated manually for unique active cart constraint

from django.conf import settings
from django.db import migrations, models


def deactivate_duplicate_active_carts(apps, schema_editor):
    Cart = apps.get_model("cart", "Cart")
    user_ids = (
        Cart.objects.filter(
            user__isnull=False,
            is_active=True,
        )
        .values_list("user_id", flat=True)
        .distinct()
    )
    for user_id in user_ids:
        carts = list(
            Cart.objects.filter(
                user_id=user_id,
                is_active=True,
            ).order_by("-id")
        )
        if len(carts) <= 1:
            continue
        Cart.objects.filter(
            pk__in=[c.pk for c in carts[1:]],
        ).update(is_active=False)


class Migration(migrations.Migration):

    dependencies = [
        ("cart", "0003_sync_model_state"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(
            deactivate_duplicate_active_carts,
            migrations.RunPython.noop,
        ),
        migrations.AddConstraint(
            model_name="cart",
            constraint=models.UniqueConstraint(
                condition=models.Q(is_active=True, user__isnull=False),
                fields=("user",),
                name="unique_active_cart_per_user",
            ),
        ),
    ]
