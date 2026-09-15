from celery import shared_task
from django.contrib.auth import get_user_model

from apps.notifications.services.notification import (
    NotificationService,
)


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
