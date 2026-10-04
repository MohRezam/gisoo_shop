from apps.notifications.models import InAppNotification, NotificationType
from apps.notifications.cache import invalidate_unread_count


def notify_user(
    *,
    user,
    title: str,
    body: str,
    type: str = NotificationType.SYSTEM,
    link: str | None = None,
    order_id: int | None = None,
    expires_at=None,
):
    if user is None:
        return None
    notif = InAppNotification.objects.create(
        user=user,
        title=title,
        body=body,
        type=type,
        link=link,
        order_id=order_id,
        expires_at=expires_at,
    )
    invalidate_unread_count(user.id)
    return notif
