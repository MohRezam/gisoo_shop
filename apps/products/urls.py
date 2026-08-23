from django.urls import path

from apps.products.apis import (
    BrandListAPIView,
    CategoryListAPIView, ProductListAPIView, ProductDetailAPIView, HairProblemAPIView, SpecialOfferProductListAPIView,
    ProductRelatedProductsAPIView,
)
from apps.products.apis.wishlist import WishlistListAPIView, WishlistToggleAPIView, WishlistItemDeleteAPIView

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
        "v1/",
        ProductListAPIView.as_view(),
        name="product-list"
    ),
    path(
        "v1/<slug:slug>/",
        ProductDetailAPIView.as_view(),
        name="product-detail",
    ),
    path(
        "v1/hair/problems/",
        HairProblemAPIView.as_view(),
        name="hair-problem",
    ),
    path(
        "v1/special/offers/",
        SpecialOfferProductListAPIView.as_view(),
        name="special-offers",
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
        "wishlist/items/<int:product_id>/",
        WishlistItemDeleteAPIView.as_view(),
        name="wishlist-item-delete",
    ),
    path(
        "products/<slug:slug>/related/",
        ProductRelatedProductsAPIView.as_view(),
        name="product-related-products",
    ),
]
