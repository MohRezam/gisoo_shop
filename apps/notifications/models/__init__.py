from .notification import Notification
from .in_app import InAppNotification, InAppNotificationType

# Inbox APIs historically imported NotificationType from models.
NotificationType = InAppNotificationType

__all__ = [
    "Notification",
    "InAppNotification",
    "InAppNotificationType",
    "NotificationType",
]
