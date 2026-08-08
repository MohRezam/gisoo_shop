from django.urls import path

from apps.notifications.apis import (
    SendOTPAPIView, VerifyOTPAPIView,
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
    ),
]
