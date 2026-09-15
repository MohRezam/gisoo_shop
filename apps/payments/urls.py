from django.urls import path

from apps.payments.apis.payment import (
    PaymentIntentCreateAPIView,
    PaymentIntentDetailAPIView,
    PaymentReceiptSubmitAPIView,
)
app_name = "apps.payments"

urlpatterns = [
    path(
        "v1/orders/<int:id>/payment-intent/",
        PaymentIntentCreateAPIView.as_view(),
        name="payment-intent-create",
    ),
    path(
        "v1/payment-intents/<uuid:token>/",
        PaymentIntentDetailAPIView.as_view(),
        name="payment-intent-detail",
    ),
    path(
        "v1/payment-intents/<int:id>/receipt/",
        PaymentReceiptSubmitAPIView.as_view(),
        name="payment-intent-receipt",
    ),
]