from django.urls import path

from apps.consultations.apis import ConsultationOptionsAPIView, ConsultationCreateAPIView, ConsultationDetailAPIView, \
    ConsultationRecommendationsAPIView

app_name = "apps.consultations"


urlpatterns = [
    path(
        "v1/options/",
        ConsultationOptionsAPIView.as_view(),
        name="options",
    ),

    path(
        "v1/",
        ConsultationCreateAPIView.as_view(),
        name="create",
    ),

    path(
        "v1/<uuid:pk>/",
        ConsultationDetailAPIView.as_view(),
        name="detail",
    ),

    path(
        "v1/<uuid:pk>/recommendations/",
        ConsultationRecommendationsAPIView.as_view(),
        name="recommendations",
    ),
]