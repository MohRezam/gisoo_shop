from django.contrib import admin
from django.urls import include, path
from django.conf import settings

admin.site.site_header = "گیسو سنتر"
admin.site.site_title = "گیسو سنتر | پنل مدیریت"
admin.site.index_title = "پیشخوان مدیریت فروشگاه"
admin.site.site_url = "https://gisoocenter.ir/"
admin.site.enable_nav_sidebar = True

admin_urlpatterns = [
    path("admin/", admin.site.urls, name="admin"),
]

if settings.DEBUG:
    admin_urlpatterns += [
        path("silk/", include("silk.urls", namespace="silk")),
        path("_nested_admin/", include("nested_admin.urls")),
        path("__debug__/", include("debug_toolbar.urls")),
    ]
