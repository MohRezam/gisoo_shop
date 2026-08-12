from django.urls import path

from apps.marketing.apis import MarketingSubscribeAPIView, MarketingVerifyOTPAPIView

app_name = "app.marketing"

urlpatterns = [
    path(
        "v1/subscribe/",
        MarketingSubscribeAPIView.as_view(),
        name="marketing-subscribe",
    ),
    path(
        "v1/subscribe/verify/",
        MarketingVerifyOTPAPIView.as_view(),
        name="marketing-subscribe-verify",
    ),
]
