from django.contrib import admin
from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from django.conf import settings

admin.site.site_title = _("core_gisoo_backend")
admin.site.index_title = _("core_gisoo_backend Platform")
admin.site.site_header = _("core_gisoo_backend")
admin.site.site_url = "https://gisoo_center.ir"

admin_urlpatterns = [
    path("admin/", admin.site.urls, name="admin"),
]

if settings.DEBUG:
    admin_urlpatterns += [
        path("silk/", include("silk.urls", namespace="silk")),
        path("_nested_admin/", include("nested_admin.urls")),
        path("__debug__/", include("debug_toolbar.urls")),
    ]
