from django.urls import path

from apps.notifications.apis import (
    SendOTPAPIView,
    VerifyOTPAPIView,
)
from apps.notifications.apis.inbox import (
    InAppNotificationListAPIView,
    UnreadNotificationCountAPIView,
    MarkNotificationReadAPIView,
    MarkAllNotificationsReadAPIView,
)

app_name = "apps.notifications"
urlpatterns = [
    path(
        "v1/send-otp/",
        SendOTPAPIView.as_view(),
        name="send-otp",
    ),
    path(
        "v1/verify-otp/",
        VerifyOTPAPIView.as_view(),
        name="verify-otp",
    ),
    path(
        "v1/",
        InAppNotificationListAPIView.as_view(),
        name="inbox-list",
    ),
    path(
        "v1/unread-count/",
        UnreadNotificationCountAPIView.as_view(),
        name="inbox-unread-count",
    ),
    path(
        "v1/read-all/",
        MarkAllNotificationsReadAPIView.as_view(),
        name="inbox-read-all",
    ),
    path(
        "v1/<int:pk>/read/",
        MarkNotificationReadAPIView.as_view(),
        name="inbox-mark-read",
    ),
]


