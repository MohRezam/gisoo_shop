from django.conf import settings
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from core_gisoo_backend.settings.components.common import DISABLE_API_DOCS

# from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet

extra_apps_urlpatterns = [
    # path(
    #     "devices/",
    #     FCMDeviceAuthorizedViewSet.as_view({"post": "create"}),
    #     name="create_fcm_device",
    # ),
    # path("ht/", include("health_check.urls")),
]

# Silk + Spectacular only when DEBUG and not explicitly disabled.
if settings.DEBUG and not DISABLE_API_DOCS:
    extra_apps_urlpatterns += [
        path("schema/", SpectacularAPIView.as_view(api_version="v1"), name="schema"),
        path(
            "docs/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        path("silk/", include("silk.urls", namespace="silk")),
    ]
