from django.conf import settings
from django.utils import timezone

from apps.notifications.constants import (
    NotificationChannel,
    NotificationStatus,
    NotificationType,
)
from apps.notifications.models import Notification, is_sms_pattern_enabled
from apps.sms.service import send_pattern_sms


class NotificationService:
    @classmethod
    def _send_via_pattern(
        cls,
        *,
        user,
        notification_type,
        recipient,
        pattern_key,
        data,
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
            if (
                pattern_key == "otp_login"
                and getattr(settings, "DEBUG", False)
            ):
                import logging

                logging.getLogger("sms").info(
                    "DEBUG OTP for %s (SMS disabled): %s",
                    recipient,
                    data.get("code"),
                )
            return notification

        if not is_sms_pattern_enabled(pattern_key):
            notification.status = NotificationStatus.FAILED
            notification.error_message = (
                f"SMS pattern '{pattern_key}' disabled in admin settings."
            )
            notification.save(update_fields=["status", "error_message"])
            return notification

        result = send_pattern_sms(
            pattern_key,
            recipient,
            data,
        )

        if result.get("success"):
            notification.status = NotificationStatus.SENT
            notification.provider_message_id = (
                result.get("message_id") or ""
            )
            notification.sent_at = timezone.now()
        else:
            notification.status = NotificationStatus.FAILED
            notification.error_message = (
                result.get("error_message") or ""
            )

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
        return cls._send_via_pattern(
            user=user,
            notification_type=NotificationType.OTP,
            recipient=recipient,
            pattern_key="otp_login",
            data={"code": str(otp)},
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
        return cls._send_via_pattern(
            user=user,
            notification_type=NotificationType.ORDER_CREATED,
            recipient=recipient,
            pattern_key="order_created",
            data={
                "order_id": str(order_id),
                "amount": str(amount),
            },
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
        return cls._send_via_pattern(
            user=user,
            notification_type=NotificationType.PAYMENT_SUCCESS,
            recipient=recipient,
            pattern_key="payment_success",
            data={
                "order_id": str(order_id),
                "amount": str(amount),
            },
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
        return cls._send_via_pattern(
            user=user,
            notification_type=NotificationType.NEW_CONSULTATION,
            recipient=recipient,
            pattern_key="new_consultation",
            data={"consultation_id": str(consultation_id)},
        )

    @classmethod
    def send_new_comment(
        cls,
        *,
        user,
        recipient,
        product_id,
    ):
        return cls._send_via_pattern(
            user=user,
            notification_type=NotificationType.NEW_COMMENT,
            recipient=recipient,
            pattern_key="new_comment",
            data={"product_id": str(product_id)},
        )

    @classmethod
    def send_order_shipped(
        cls,
        *,
        user,
        recipient,
        order_id,
    ):
        return cls._send_via_pattern(
            user=user,
            notification_type=NotificationType.ORDER_SHIPPED,
            recipient=recipient,
            pattern_key="order_shipped",
            data={"order_id": str(order_id)},
        )

    @classmethod
    def send_order_cancelled(
        cls,
        *,
        user,
        recipient,
        order_id,
    ):
        return cls._send_via_pattern(
            user=user,
            notification_type=NotificationType.ORDER_CANCELLED,
            recipient=recipient,
            pattern_key="order_cancelled",
            data={"order_id": str(order_id)},
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
        return cls._send_via_pattern(
            user=user,
            notification_type=NotificationType.PAYMENT_REMINDER,
            recipient=recipient,
            pattern_key="payment_reminder",
            data={
                "order_id": str(order_id),
                "minutes_left": str(minutes_left),
            },
            idempotency_key=idempotency_key,
        )

    @classmethod
    def send_delivery_confirm(
        cls,
        *,
        user,
        recipient,
        order_id,
        idempotency_key=None,
    ):
        return cls._send_via_pattern(
            user=user,
            notification_type=NotificationType.DELIVERY_CONFIRM,
            recipient=recipient,
            pattern_key="delivery_confirm",
            data={"order_id": str(order_id)},
            idempotency_key=idempotency_key,
        )
