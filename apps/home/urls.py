from django.urls import path

from apps.home.apis import BannerAPIView, HomeAboutAPIView

app_name = "apps.home"

urlpatterns = [
    path(
        "v1/banner/slides/",
        BannerAPIView.as_view(),
        name="banner",
    ),
    path(
        "v1/about/",
        HomeAboutAPIView.as_view(),
        name="about",
    ),
]
