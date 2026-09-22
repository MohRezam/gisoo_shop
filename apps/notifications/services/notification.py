from django.conf import settings
from django.utils import timezone

from apps.notifications.constants import (
    NotificationChannel,
    NotificationStatus,
    NotificationType,
)
from apps.notifications.models import Notification
from apps.notifications.services.sms import (
    MelipayamakProvider,
)


class NotificationService:

    sms_provider = MelipayamakProvider()

    @classmethod
    def send_sms_pattern(
            cls,
            *,
            user,
            notification_type,
            recipient,
            pattern_id,
            args,
            idempotency_key=None,
    ):
        if idempotency_key:
            existing_notification = (
                Notification.objects
                .filter(idempotency_key=idempotency_key)
                .first()
            )

            if existing_notification:
                return existing_notification

        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            channel=NotificationChannel.SMS,
            recipient=recipient,
            status=NotificationStatus.PENDING,
            idempotency_key=idempotency_key,
        )

        if not getattr(settings, "SMS_ENABLED", False):
            notification.status = NotificationStatus.FAILED
            notification.error_message = "SMS_ENABLED is False; SMS not sent."
            notification.save(
                update_fields=["status", "error_message"]
            )
            return notification

        if not pattern_id:
            notification.status = NotificationStatus.FAILED
            notification.error_message = "SMS pattern id is not configured."
            notification.save(
                update_fields=["status", "error_message"]
            )
            return notification

        result = cls.sms_provider.send_pattern(
            recipient=recipient,
            pattern_id=pattern_id,
            args=args,
        )

        if result.success:
            notification.status = NotificationStatus.SENT
            notification.provider_message_id = (
                    result.provider_message_id or ""
            )
            notification.sent_at = timezone.now()
        else:
            notification.status = NotificationStatus.FAILED
            notification.error_message = result.error or ""

        notification.save(
            update_fields=[
                "status",
                "provider_message_id",
                "error_message",
                "sent_at",
            ]
        )

        return notification

    @classmethod
    def send_otp(
        cls,
        *,
        user,
        recipient,
        otp,
    ):
        pattern_id = settings.SMS_PATTERN_OTP

        return cls.send_sms_pattern(
            user=user,
            notification_type=(
                NotificationType.OTP
            ),
            recipient=recipient,
            pattern_id=pattern_id,
            args=[
                otp,
            ],
        )

    @classmethod
    def send_order_created(
        cls,
        *,
        user,
        recipient,
        order_id,
        amount,
    ):
        pattern_id = (
            settings.SMS_PATTERN_ORDER_CREATED
        )

        return cls.send_sms_pattern(
            user=user,
            notification_type=(
                NotificationType.ORDER_CREATED
            ),
            recipient=recipient,
            pattern_id=pattern_id,
            args=[
                str(order_id),
                str(amount),
            ],
        )

    @classmethod
    def send_payment_success(
            cls,
            *,
            user,
            recipient,
            order_id,
            amount,
    ):
        pattern_id = (
            settings.SMS_PATTERN_PAYMENT_SUCCESS
        )

        return cls.send_sms_pattern(
            user=user,
            notification_type=(
                NotificationType.PAYMENT_SUCCESS
            ),
            recipient=recipient,
            pattern_id=pattern_id,
            args=[
                str(order_id),
                str(amount),
            ],
            idempotency_key=f"payment_success:{order_id}",
        )

    @classmethod
    def send_new_consultation(
        cls,
        *,
        user,
        recipient,
        consultation_id,
    ):
        pattern_id = (
            settings.SMS_PATTERN_NEW_CONSULTATION
        )

        return cls.send_sms_pattern(
            user=user,
            notification_type=(
                NotificationType.NEW_CONSULTATION
            ),
            recipient=recipient,
            pattern_id=pattern_id,
            args=[
                str(consultation_id),
            ],
        )

    @classmethod
    def send_new_comment(
        cls,
        *,
        user,
        recipient,
        product_id,
    ):
        pattern_id = (
            settings.SMS_PATTERN_NEW_COMMENT
        )

        return cls.send_sms_pattern(
            user=user,
            notification_type=(
                NotificationType.NEW_COMMENT
            ),
            recipient=recipient,
            pattern_id=pattern_id,
            args=[
                str(product_id),
            ],
        )

    @classmethod
    def send_new_image(
        cls,
        *,
        user,
        recipient,
        consultation_id,
    ):
        pattern_id = (
            settings.SMS_PATTERN_NEW_IMAGE
        )

        return cls.send_sms_pattern(
            user=user,
            notification_type=(
                NotificationType.NEW_IMAGE
            ),
            recipient=recipient,
            pattern_id=pattern_id,
            args=[
                str(consultation_id),
            ],
        )

    @classmethod
    def send_order_shipped(
        cls,
        *,
        user,
        recipient,
        order_id,
    ):
        pattern_id = (
            settings.SMS_PATTERN_ORDER_SHIPPED
        )

        return cls.send_sms_pattern(
            user=user,
            notification_type=(
                NotificationType.ORDER_SHIPPED
            ),
            recipient=recipient,
            pattern_id=pattern_id,
            args=[
                str(order_id),
            ],
        )

    @classmethod
    def send_order_cancelled(
        cls,
        *,
        user,
        recipient,
        order_id,
    ):
        pattern_id = (
            settings.SMS_PATTERN_ORDER_CANCELLED
        )

        return cls.send_sms_pattern(
            user=user,
            notification_type=(
                NotificationType.ORDER_CANCELLED
            ),
            recipient=recipient,
            pattern_id=pattern_id,
            args=[
                str(order_id),
            ],
        )

    @classmethod
    def send_payment_reminder(
        cls,
        *,
        user,
        recipient,
        order_id,
        minutes_left,
        idempotency_key=None,
    ):
        pattern_id = getattr(
            settings,
            "SMS_PATTERN_PAYMENT_REMINDER",
            0,
        )
        return cls.send_sms_pattern(
            user=user,
            notification_type=(
                NotificationType.PAYMENT_REMINDER
            ),
            recipient=recipient,
            pattern_id=pattern_id,
            args=[
                str(order_id),
                str(minutes_left),
            ],
            idempotency_key=idempotency_key,
        )
