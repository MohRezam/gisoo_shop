from django.urls import path

from apps.orders.apis import (
    CreateOrderAPIView,
    LatestOrderAPIView,
    OrderDetailAPIView,
    OrderListAPIView,
)

app_name = "apps.orders"

urlpatterns = [
    path(
        "v1/",
        CreateOrderAPIView.as_view(),
        name="create-order",
    ),
    path(
        "v1/my/",
        OrderListAPIView.as_view(),
        name="order-list",
    ),
    path(
        "v1/my/latest/",
        LatestOrderAPIView.as_view(),
        name="latest-order",
    ),
    path(
        "v1/<int:id>/",
        OrderDetailAPIView.as_view(),
        name="order-detail",
    ),
]