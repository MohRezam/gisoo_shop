from django.urls import path

from apps.cart.apis import CartDetailAPIView, UpdateCartItemAPIView, DeleteCartItemAPIView, AddToCartAPIView

app_name = "apps.cart"

urlpatterns = [
    path(
        "v1/<uuid:uuid>/",
        CartDetailAPIView.as_view(),
        name="cart-detail",
    ),
    path(
        "items/v1/<int:item_id>/update/",
        UpdateCartItemAPIView.as_view(),
        name="cart-item-update",
    ),

    path(
        "items/v1/<int:item_id>/delete/",
        DeleteCartItemAPIView.as_view(),
        name="cart-item-delete",
    ),
    path(
        "add/v1/",
        AddToCartAPIView.as_view(),
        name="add-to-cart",
    ),
]
