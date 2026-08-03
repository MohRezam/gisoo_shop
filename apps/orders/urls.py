from django.urls import path

from apps.orders.apis import (
    CreateOrderAPIView, OrderDetailAPIView,
)

app_name="apps.orders"

urlpatterns = [
    path(
        "v1/",
        CreateOrderAPIView.as_view(),
        name="create-order",
    ),
    path(
        "v1/<int:id>/",
        OrderDetailAPIView.as_view(),
        name="order-detail",
    ),
]
