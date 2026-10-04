from apps.notifications.models import AdminAlert, AdminAlertType


def notify_admin(
    *,
    title: str,
    body: str = "",
    type: str = AdminAlertType.SYSTEM,
    link: str = "",
):
    return AdminAlert.objects.create(
        title=title,
        body=body,
        type=type,
        link=link or "",
    )
