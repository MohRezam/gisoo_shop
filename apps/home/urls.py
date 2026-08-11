from django.urls import path

from apps.home.apis import BannerAPIView, HomeAboutAPIView
from apps.home.apis.customer_satisfaction import CustomerSatisfactionListAPIView
from apps.home.apis.frequently_asked_questions import FAQListAPIView

app_name = "apps.home"

urlpatterns = [
    path(
        "v1/banner/slides/",
        BannerAPIView.as_view(),
        name="banner",
    ),
    path(
        "v1/about/",
        HomeAboutAPIView.as_view(),
        name="about",
    ),
    path(
        "v1/customer/satisfaction/",
        CustomerSatisfactionListAPIView.as_view(),
        name="customer-satisfaction-list",
    ),
    path(
        "v1/faqs/",
        FAQListAPIView.as_view(),
        name="faq-list",
    ),
]
