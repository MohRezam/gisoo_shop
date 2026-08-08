from django.urls import path

from apps.payments.apis import (
    PaymentDetailAPIView,
    StartPaymentAPIView,
    GatewayCallbackAPIView,
)
app_name = "apps.payments"
urlpatterns = [
    path(
        "v1/<int:payment_id>/",
        PaymentDetailAPIView.as_view(),
        name="payment-detail",
    ),

    path(
        "v1/<int:payment_id>/start/",
        StartPaymentAPIView.as_view(),
        name="start-payment",
    ),

    path(
        "v1/callback/",
        GatewayCallbackAPIView.as_view(),
        name="payment-callback",
    ),
]
