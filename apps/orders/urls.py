from django.urls import path

from apps.orders.apis import (
    CreateOrderAPIView,
    OrderDetailAPIView,
    MyOrdersListAPIView,
    MyLatestOrderAPIView,
    TrackOrderAPIView,
)

app_name = "apps.orders"

urlpatterns = [
    path(
        "v1/my/",
        MyOrdersListAPIView.as_view(),
        name="my-orders",
    ),
    path(
        "v1/my/latest/",
        MyLatestOrderAPIView.as_view(),
        name="my-latest-order",
    ),
    path(
        "v1/track/",
        TrackOrderAPIView.as_view(),
        name="track-order",
    ),
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