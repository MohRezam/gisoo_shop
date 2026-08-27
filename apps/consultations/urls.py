from django.urls import path

from apps.consultations.apis import (
    ConsultationOptionsAPIView,
    ConsultationCreateAPIView,
    ConsultationListAPIView,
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
]
