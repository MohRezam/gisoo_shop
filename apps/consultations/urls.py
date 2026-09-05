from django.urls import path

from apps.consultations.apis import (
    ConsultationCreateAPIView,
    ConsultationListAPIView,
    ConsultationOptionsAPIView,
    ConsultationUpdateAPIView,
)


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
        "<uuid:pk>/",
        ConsultationUpdateAPIView.as_view(),
        name="detail",
    ),
]