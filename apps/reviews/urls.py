from django.urls import path

from apps.reviews.apis import ProductReviewListCreateAPIView, HomepageReviewListAPIView

app_name = "apps.reviews"

urlpatterns = [
    path(
        "products/<int:product_id>/reviews/",
        ProductReviewListCreateAPIView.as_view(),
        name="product-reviews",
    ),

    path(
        "reviews/homepage/",
        HomepageReviewListAPIView.as_view(),
        name="homepage-reviews",
    ),
]
