from django.urls import path

from apps.consultations.apis import (
    ConsultationCreateAPIView,
    ConsultationListAPIView,
    ConsultationOptionsAPIView,
    ConsultationUpdateAPIView, AddAllRecommendationsToCartAPIView, AddSelectedRecommendationsToCartAPIView,
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
    path(
        "<uuid:pk>/recommendations/add-all-to-cart/",
        AddAllRecommendationsToCartAPIView.as_view(),
        name="consultation-add-all-recommendations-to-cart",
    ),

    path(
        "<uuid:pk>/recommendations/add-selected-to-cart/",
        AddSelectedRecommendationsToCartAPIView.as_view(),
        name="consultation-add-selected-recommendations-to-cart",
    ),
]
