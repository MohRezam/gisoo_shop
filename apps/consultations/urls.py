from django.urls import path

from apps.consultations.apis import ConsultationOptionsAPIView, ConsultationCreateAPIView, ConsultationListAPIView, \
    GuestOTPRequestAPIView, GuestOTPVerifyAPIView, ConsultationDetailAPIView, ConsultationRecommendationsAPIView

app_name = "apps.consultations"

urlpatterns = [
    path(
        "options/",
        ConsultationOptionsAPIView.as_view(),
        name="options",
    ),

    path(
        "",
        ConsultationCreateAPIView.as_view(),
        name="create",
    ),

    path(
        "my/",
        ConsultationListAPIView.as_view(),
        name="my",
    ),

    path(
        "guest/access/request/",
        GuestOTPRequestAPIView.as_view(),
        name="guest-access-request",
    ),

    path(
        "guest/access/verify/",
        GuestOTPVerifyAPIView.as_view(),
        name="guest-access-verify",
    ),

    path(
        "<uuid:pk>/",
        ConsultationDetailAPIView.as_view(),
        name="detail",
    ),

    path(
        "<uuid:pk>/recommendations/",
        ConsultationRecommendationsAPIView.as_view(),
        name="recommendations",
    ),
]
