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
    retry_kwargs={"max_retries": 3},
)
def send_order_shipped_sms(user_id, recipient, order_id):
    User = get_user_model()
    user = User.objects.get(id=user_id)
    notification = NotificationService.send_order_shipped(
        user=user,
        recipient=recipient,
        order_id=order_id,
    )
    return notification.id


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_kwargs={"max_retries": 3},
)
def send_order_cancelled_sms(user_id, recipient, order_id):
    User = get_user_model()
    user = User.objects.get(id=user_id)
    notification = NotificationService.send_order_cancelled(
        user=user,
        recipient=recipient,
        order_id=order_id,
    )
    return notification.id


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_kwargs={"max_retries": 3},
)
def send_consultation_answered_sms(
    user_id,
    recipient,
    consultation_id,
):
    User = get_user_model()
    user = None
    if user_id:
        user = User.objects.filter(id=user_id).first()

    notification = NotificationService.send_consultation_answered(
        user=user,
        recipient=recipient,
        consultation_id=consultation_id,
        idempotency_key=f"consultation_answered:{consultation_id}",
    )
    return notification.id


def _order_status_sms_task(
    *,
    user_id,
    recipient,
    order_id,
    send_fn,
    idempotency_key=None,
):
    User = get_user_model()
    user = User.objects.get(id=user_id)
    kwargs = {
        "user": user,
        "recipient": recipient,
        "order_id": order_id,
    }
    if idempotency_key is not None:
        kwargs["idempotency_key"] = idempotency_key
    notification = send_fn(**kwargs)
    return notification.id


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_kwargs={"max_retries": 3},
)
def send_order_preparing_sms(user_id, recipient, order_id):
    return _order_status_sms_task(
        user_id=user_id,
        recipient=recipient,
        order_id=order_id,
        send_fn=NotificationService.send_order_preparing,
    )


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_kwargs={"max_retries": 3},
)
def send_order_expired_sms(user_id, recipient, order_id):
    return _order_status_sms_task(
        user_id=user_id,
        recipient=recipient,
        order_id=order_id,
        send_fn=NotificationService.send_order_expired,
        idempotency_key=f"order_expired:{order_id}",
    )


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_kwargs={"max_retries": 3},
)
def send_payment_rejected_sms(user_id, recipient, order_id):
    return _order_status_sms_task(
        user_id=user_id,
        recipient=recipient,
        order_id=order_id,
        send_fn=NotificationService.send_payment_rejected,
        idempotency_key=f"payment_rejected:{order_id}",
    )


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_kwargs={"max_retries": 3},
)
def send_consultation_received_sms(
    user_id,
    recipient,
    consultation_id,
):
    User = get_user_model()
    user = None
    if user_id:
        user = User.objects.filter(id=user_id).first()

    notification = NotificationService.send_consultation_received(
        user=user,
        recipient=recipient,
        consultation_id=consultation_id,
        idempotency_key=f"consultation_received:{consultation_id}",
    )
    return notification.id


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


@shared_task
def purge_old_read_admin_alerts():
    """
    Delete admin alerts that staff already read, older than 2 weeks.
    Unread alerts are kept so nothing important is lost.
    """
    from datetime import timedelta

    from apps.notifications.models import AdminAlert

    cutoff = timezone.now() - timedelta(days=READ_NOTIFICATION_RETENTION_DAYS)
    deleted, _ = AdminAlert.objects.filter(
        is_read=True,
        created_at__lte=cutoff,
    ).delete()
    return deleted
