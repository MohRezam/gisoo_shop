from django.urls import path

from apps.products.apis import (
    BrandListAPIView,
    CategoryListAPIView,
    ProductListAPIView,
    ProductDetailAPIView,
    HairProblemAPIView,
    HairTypeAPIView,
    ProductFiltersMetaAPIView,
    SpecialOfferProductListAPIView,
    ProductRelatedProductsAPIView,
    ProductViewerAPIView,
)
from apps.products.apis.discount_campaign import ActiveDiscountCampaignView
from apps.products.apis.wishlist import (
    WishlistListAPIView,
    WishlistToggleAPIView,
    WishlistItemDeleteAPIView,
)
from apps.products.apis.stock_notify import WishlistStockNotifyAPIView
from apps.products.apis.consultation import (
    ConsultationRecommendationsAPIView,
    DiscountCampaignsAPIView,
)

app_name = "apps.products"

urlpatterns = [
    path(
        "v1/categories/",
        CategoryListAPIView.as_view(),
        name="category-list",
    ),
    path(
        "v1/brands/",
        BrandListAPIView.as_view(),
        name="brand-list",
    ),
    path(
        "v1/hair/problems/",
        HairProblemAPIView.as_view(),
        name="hair-problem",
    ),
    path(
        "v1/hair/types/",
        HairTypeAPIView.as_view(),
        name="hair-type",
    ),
    path(
        "v1/filters/",
        ProductFiltersMetaAPIView.as_view(),
        name="product-filters-meta",
    ),
    path(
        "v1/special/offers/",
        SpecialOfferProductListAPIView.as_view(),
        name="special-offers",
    ),
    path(
        "v1/discount-campaigns/",
        DiscountCampaignsAPIView.as_view(),
        name="discount-campaigns",
    ),
    path(
        "v1/consultation/recommendations/",
        ConsultationRecommendationsAPIView.as_view(),
        name="consultation-recommendations",
    ),
    path(
        "v1/",
        ProductListAPIView.as_view(),
        name="product-list",
    ),
    path(
        "v1/<slug:slug>/",
        ProductDetailAPIView.as_view(),
        name="product-detail",
    ),
    path(
        "wishlist/",
        WishlistListAPIView.as_view(),
        name="wishlist-list",
    ),
    path(
        "wishlist/toggle/",
        WishlistToggleAPIView.as_view(),
        name="wishlist-toggle",
    ),
    path(
        "wishlist/notify-stock/",
        WishlistStockNotifyAPIView.as_view(),
        name="wishlist-notify-stock",
    ),
    path(
        "wishlist/items/<int:product_id>/",
        WishlistItemDeleteAPIView.as_view(),
        name="wishlist-item-delete",
    ),
    path(
        "products/<slug:slug>/related/",
        ProductRelatedProductsAPIView.as_view(),
        name="product-related-products",
    ),
    path(
        "products/<slug:slug>/viewers/",
        ProductViewerAPIView.as_view(),
        name="product-viewers",
    ),
    path(
        "discount-campaigns/",
        ActiveDiscountCampaignView.as_view(),
        name="active-discount-campaigns",
    ),
]
