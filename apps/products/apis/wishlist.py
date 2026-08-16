from django.db.models import Prefetch
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.products.models import (
    Product,
    ProductVariant,
    WishlistItem,
)
from apps.products.serializers.wishlist import (
    WishlistItemSerializer,
)
from apps.products.services.wishlist import (
    WishlistService,
)
from core_gisoo_backend.settings.components.constants import WISHLIST_COOKIE_NAME, WISHLIST_COOKIE_MAX_AGE


class WishlistBaseAPIView(APIView):
    permission_classes = [AllowAny]

    def get_wishlist(self):
        if self.request.user.is_authenticated:
            wishlist, _ = (
                WishlistService.get_or_create_user_wishlist(
                    self.request.user
                )
            )

            return wishlist, False

        token = self.request.COOKIES.get(
            WISHLIST_COOKIE_NAME
        )

        wishlist, created = (
            WishlistService.get_or_create_guest_wishlist(
                token
            )
        )

        return wishlist, created

    def set_guest_cookie(self, response, wishlist):
        response.set_cookie(
            key=WISHLIST_COOKIE_NAME,
            value=str(wishlist.guest_token),
            max_age=WISHLIST_COOKIE_MAX_AGE,
            httponly=True,
            secure=True,
            samesite="Lax",
        )

        return response


class WishlistListAPIView(WishlistBaseAPIView):

    def get(self, request):
        wishlist, created = self.get_wishlist()

        wishlist_items = (
            WishlistItem.objects
            .filter(
                wishlist=wishlist,
            )
            .select_related(
                "product",
            )
            .prefetch_related(
                "product__images",
                Prefetch(
                    "product__variants",
                    queryset=ProductVariant.objects.filter(
                        is_active=True
                    ),
                ),
            )
            .order_by("-created_at")
        )

        serializer = WishlistItemSerializer(
            wishlist_items,
            many=True,
            context={
                "request": request,
            },
        )

        response = Response({
            "count": wishlist_items.count(),
            "items": serializer.data,
        })

        if created and not request.user.is_authenticated:
            self.set_guest_cookie(
                response,
                wishlist,
            )

        return response


class WishlistToggleAPIView(WishlistBaseAPIView):

    def post(self, request):
        product_id = request.data.get("product")

        if not product_id:
            return Response(
                {
                    "detail": "Product is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            product = Product.objects.get(
                pk=product_id,
                is_available=True,
            )
        except Product.DoesNotExist:
            return Response(
                {
                    "detail": "Product not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        wishlist, created = self.get_wishlist()

        result = WishlistService.toggle_product(
            wishlist=wishlist,
            product=product,
        )

        response = Response(result)

        if created and not request.user.is_authenticated:
            self.set_guest_cookie(
                response,
                wishlist,
            )

        return response


class WishlistItemDeleteAPIView(
    WishlistBaseAPIView
):

    def delete(self, request, product_id):
        wishlist, created = self.get_wishlist()

        deleted_count, _ = (
            WishlistItem.objects
            .filter(
                wishlist=wishlist,
                product_id=product_id,
            )
            .delete()
        )

        if deleted_count == 0:
            return Response(
                {
                    "detail": "Product is not in wishlist."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        response = Response(
            status=status.HTTP_204_NO_CONTENT
        )

        if created and not request.user.is_authenticated:
            self.set_guest_cookie(
                response,
                wishlist,
            )

        return response
