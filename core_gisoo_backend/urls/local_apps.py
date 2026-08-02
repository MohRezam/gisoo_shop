from django.urls import include, path

local_apps_urlpatterns = [
    path("users/", include("apps.users.urls", namespace="apps.users")),
    path(
        "notifications/",
        include("apps.notifications.urls", namespace="apps.notifications"),
    ),
]
