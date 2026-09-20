from django.urls import path

from apps.payments.apis.payment import (
    PaymentIntentCreateAPIView,
    PaymentIntentDetailAPIView,
    PaymentReceiptSubmitAPIView,
)
from apps.payments.apis.payment_intent import (
    CreatePaymentIntentAPIView,
    PaymentIntentByTokenAPIView,
    UploadPaymentReceiptAPIView,
)

app_name = "apps.payments"

urlpatterns = [
    path(
        "v1/orders/<int:order_id>/payment-intent/",
        CreatePaymentIntentAPIView.as_view(),
        name="create-payment-intent",
    ),
    path(
        "v1/payment-intents/<str:token>/",
        PaymentIntentByTokenAPIView.as_view(),
        name="payment-intent-by-token",
    ),
    path(
        "v1/payment-intents/<int:intent_id>/receipt/",
        UploadPaymentReceiptAPIView.as_view(),
        name="upload-payment-receipt",
    ),
    path(
        "v1/<int:payment_id>/",
        PaymentDetailAPIView.as_view(),
        name="payment-detail",
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