from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.users.apis import ProfileSummaryAPIView, ProfileAPIView, \
    PhoneNumberListAPIView, PhoneNumberDetailAPIView, SetPrimaryPhoneNumberAPIView, AddPhoneNumberVerifyOTPAPIView, \
    AddPhoneNumberRequestOTPAPIView
from apps.users.apis.login import RequestOTPAPIView, ResendOTPAPIView, VerifyOTPAPIView
from apps.users.apis.logout import BlacklistRefreshAPIView

app_name = "apps.users"

urlpatterns = [
    # login
    path("v1/otp/request/", RequestOTPAPIView.as_view(), name="otp-request"),
    path("v1/otp/request/resend/", ResendOTPAPIView.as_view(), name="otp-resend"),
    path("v1/otp/verify/", VerifyOTPAPIView.as_view(), name="otp-verify"),
    path("v1/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    # logout
    path("v1/logout/", BlacklistRefreshAPIView.as_view(), name="user-logout"),

    # profile
    path(
        "v1/profile/summary/",
        ProfileSummaryAPIView.as_view(),
        name="profile-summary",
    ),

    path(
        "v1/profile/",
        ProfileAPIView.as_view(),
        name="profile",
    ),

    # Phone numbers
    path(
        "profile/phone-numbers/",
        PhoneNumberListAPIView.as_view(),
        name="phone-number-list",
    ),
    path(
        "profile/phone-numbers/request-otp/",
        AddPhoneNumberRequestOTPAPIView.as_view(),
        name="phone-number-request-otp",
    ),
    path(
        "profile/phone-numbers/verify-otp/",
        AddPhoneNumberVerifyOTPAPIView.as_view(),
        name="phone-number-verify-otp",
    ),
    path(
        "profile/phone-numbers/<int:pk>/",
        PhoneNumberDetailAPIView.as_view(),
        name="phone-number-detail",
    ),
    path(
        "profile/phone-numbers/<int:pk>/set-primary/",
        SetPrimaryPhoneNumberAPIView.as_view(),
        name="phone-number-set-primary",
    ),
]
