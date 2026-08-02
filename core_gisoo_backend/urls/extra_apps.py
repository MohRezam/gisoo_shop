from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet

extra_apps_urlpatterns = [
    # path(
    #     "devices/",
    #     FCMDeviceAuthorizedViewSet.as_view({"post": "create"}),
    #     name="create_fcm_device",
    # ),
    # path("ht/", include("health_check.urls")),
]

extra_apps_urlpatterns += [
    path("schema/", SpectacularAPIView.as_view(api_version="v1"), name="schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(),
        name="swagger-ui",
    ),
]
