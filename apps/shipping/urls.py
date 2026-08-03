from django.urls import path

from apps.shipping.apis import (
    ShippingMethodListAPIView,
)
app_name = "apps.shipping"
urlpatterns = [
    path(
        "v1/methods/",
        ShippingMethodListAPIView.as_view(),
        name="shipping-methods",
    ),
]
