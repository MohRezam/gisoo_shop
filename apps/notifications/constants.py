from django.db import models


class NotificationType(models.TextChoices):
    OTP = "OTP", "OTP"

    ORDER_CREATED = (
        "ORDER_CREATED",
        "Order Created",
    )

    PAYMENT_SUCCESS = (
        "PAYMENT_SUCCESS",
        "Payment Success",
    )

    NEW_CONSULTATION = (
        "NEW_CONSULTATION",
        "New Consultation",
    )

    NEW_COMMENT = (
        "NEW_COMMENT",
        "New Comment",
    )

    NEW_IMAGE = (
        "NEW_IMAGE",
        "New Image",
    )

    ORDER_SHIPPED = (
        "ORDER_SHIPPED",
        "Order Shipped",
    )

    ORDER_CANCELLED = (
        "ORDER_CANCELLED",
        "Order Cancelled",
    )


class NotificationChannel(models.TextChoices):
    SMS = "SMS", "SMS"
    EMAIL = "EMAIL", "Email"
    PUSH = "PUSH", "Push"
    IN_APP = "IN_APP", "In App"


class NotificationStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    SENT = "SENT", "Sent"
    FAILED = "FAILED", "Failed"