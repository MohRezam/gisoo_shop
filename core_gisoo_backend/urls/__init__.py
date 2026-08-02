from logging import getLogger

from django.conf import settings
from django.urls import path, include

from .admin_configs import admin_urlpatterns
from .extra_apps import extra_apps_urlpatterns
from .local_apps import local_apps_urlpatterns

# Logging
logger = getLogger("custom")

hidden = admin_urlpatterns
v1 = local_apps_urlpatterns + extra_apps_urlpatterns

urlpatterns = [
    path("", include(hidden)),
    path("api/", include(v1)),
]

if settings.DEBUG:
    import debug_toolbar
    from django.conf.urls.static import static
    from django.urls import include, path

    def get_server_time(request, *args, **kwargs):
        from django.http import HttpResponse
        from django.utils.timezone import now

        return HttpResponse(f"Server time: {now()}")

    urlpatterns.append(path("get_server_time", get_server_time, name="get_server_time"))
    urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
