from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.users.apis.login import RequestOTPAPIView, ResendOTPAPIView, VerifyOTPAPIView
from apps.users.apis.logout import BlacklistRefreshAPIView

app_name = "apps.users"

urlpatterns = [
    # login
    path("v1/otp/request/", RequestOTPAPIView.as_view(), name="otp-request"),
    path("v1/otp/request/resend/", ResendOTPAPIView.as_view(), name="otp-resend"),
    path("v1/otp/verify/", VerifyOTPAPIView.as_view(), name="otp-verify"),
    path("v1/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("v1/token/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    # logout
    path("v1/logout/", BlacklistRefreshAPIView.as_view(), name="user-logout"),
]
