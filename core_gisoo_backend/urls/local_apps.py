from django.urls import include, path

local_apps_urlpatterns = [
    path("users/", include("apps.users.urls", namespace="apps.users")),
    path(
        "notifications/",
        include("apps.notifications.urls", namespace="apps.notifications"),
    ),
    path(
        "products/",
        include("apps.products.urls", namespace="apps.products"),
    ),
    path(
        "addresses/",
        include("apps.addresses.urls", namespace="apps.addresses"),
    ),
    path(
        "orders/",
        include("apps.orders.urls", namespace="apps.orders"),
    ),
    path(
        "payments/",
        include("apps.payments.urls", namespace="apps.payments"),
    ),
    path(
        "shipping/",
        include("apps.shipping.urls", namespace="apps.shipping"),
    ),
    path(
        "cart/",
        include("apps.cart.urls", namespace="apps.cart"),
    ),
    path(
        "home/",
        include("apps.home.urls", namespace="apps.home")
    ),
    path(
        "magazine/",
        include("apps.magazine.urls", namespace="apps.magazine")
    ),
    path(
        "marketing/",
        include("apps.marketing.urls", namespace="apps.marketing")
    ),
    path(
        "consultations/",
        include("apps.consultations.urls", namespace="apps.consultations"),
    ),

]
