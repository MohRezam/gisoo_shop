from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.notifications.services.notification import (
    NotificationService,
)


READ_NOTIFICATION_RETENTION_DAYS = 14


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_kwargs={
        "max_retries": 3,
    },
)
def send_order_created_sms(
        user_id,
        recipient,
        order_id,
        amount,
):
    from django.contrib.auth import get_user_model

    User = get_user_model()

    user = User.objects.get(
        id=user_id
    )

    return NotificationService.send_order_created(
        user=user,
        recipient=recipient,
        order_id=order_id,
        amount=amount,
    )


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_kwargs={"max_retries": 3},
)
def send_payment_success_sms(user_id, recipient, order_id, amount):
    User = get_user_model()
    user = User.objects.get(id=user_id)

    notification = NotificationService.send_payment_success(
        user=user,
        recipient=recipient,
        order_id=order_id,
        amount=amount,
    )

    return notification.id


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_kwargs={
        "max_retries": 3,
    },
)
def send_new_consultation_sms(
        user_id,
        recipient,
        consultation_id,
):
    from django.contrib.auth import get_user_model

    User = get_user_model()

    user = User.objects.get(
        id=user_id
    )

    return NotificationService.send_new_consultation(
        user=user,
        recipient=recipient,
        consultation_id=consultation_id,
    )


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_kwargs={
        "max_retries": 3,
    },
)
def send_new_comment_sms(
        user_id,
        recipient,
        product_id,
):
    from django.contrib.auth import get_user_model

    User = get_user_model()

    user = User.objects.get(
        id=user_id
    )

    return NotificationService.send_new_comment(
        user=user,
        recipient=recipient,
        product_id=product_id,
    )


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_kwargs={
        "max_retries": 3,
    },
)
def send_new_image_sms(
        user_id,
        recipient,
        consultation_id,
):
    from django.contrib.auth import get_user_model

    User = get_user_model()

    user = User.objects.get(
        id=user_id
    )

    return NotificationService.send_new_image(
        user=user,
        recipient=recipient,
        consultation_id=consultation_id,
    )


@shared_task
def purge_old_read_in_app_notifications():
    """
    Delete read in-app notifications older than 2 weeks (by created_at).
    Unread notifications are kept regardless of age.
    """
    from datetime import timedelta

    from apps.notifications.models import InAppNotification

    cutoff = timezone.now() - timedelta(days=READ_NOTIFICATION_RETENTION_DAYS)
    deleted, _ = InAppNotification.objects.filter(
        is_read=True,
        created_at__lte=cutoff,
    ).delete()
    return deleted
