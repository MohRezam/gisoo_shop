from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone

from apps.notifications.services.inbox import notify_user
from apps.products.models import ProductVariant
from apps.products.models.stock_notify import WishlistStockNotify


@receiver(pre_save, sender=ProductVariant)
def cache_previous_stock(sender, instance: ProductVariant, **kwargs):
    if not instance.pk:
        instance._previous_stock = 0
        return
    try:
        previous = ProductVariant.objects.get(pk=instance.pk)
        instance._previous_stock = previous.stock
    except ProductVariant.DoesNotExist:
        instance._previous_stock = 0


@receiver(post_save, sender=ProductVariant)
def notify_back_in_stock(sender, instance: ProductVariant, **kwargs):
    previous = getattr(instance, "_previous_stock", 0)
    if previous > 0 or instance.stock <= 0:
        return

    pending = WishlistStockNotify.objects.filter(
        product_id=instance.product_id,
        is_notified=False,
        user__isnull=False,
    ).select_related("user", "product")

    for req in pending:
        notify_user(
            user=req.user,
            title="موجود شد",
            body=f'محصول «{req.product.title}» دوباره موجود شد.',
            type="stock",
            link=f"/products/{req.product.slug}",
            order_id=None,
        )
        req.is_notified = True
        req.notified_at = timezone.now()
        req.save(update_fields=["is_notified", "notified_at", "updated_at"])
