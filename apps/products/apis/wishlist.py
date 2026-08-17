from django.db.models import Prefetch

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
)

from apps.products.models import (
    Product,
    ProductVariant,
    WishlistItem,
)
from apps.products.serializers import WishlistDeleteResponseSerializer

from apps.products.serializers.wishlist import (
    WishlistItemSerializer,
    WishlistSerializer,
    WishlistToggleSerializer,
    WishlistToggleResponseSerializer,
)

from apps.products.services.wishlist import (
    WishlistService,
)

from core_gisoo_backend.settings.components.constants import (
    WISHLIST_COOKIE_NAME,
    WISHLIST_COOKIE_MAX_AGE,
)


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
            secure=False,
            samesite="Lax",
        )

        return response


class WishlistListAPIView(WishlistBaseAPIView):

    @extend_schema(
        tags=["Wishlist"],
        summary="Retrieve Wishlist",
        description=(
            "Retrieve the current user's wishlist. "
            "Authenticated users receive their account wishlist. "
            "Guest users receive their wishlist using the "
            "`wishlist_token` cookie."
        ),
        responses={
            200: OpenApiResponse(
                response=WishlistSerializer,
                description="Wishlist retrieved successfully.",
                examples=[
                    OpenApiExample(
                        name="Wishlist",
                        summary="Wishlist with products",
                        value={
                            "count": 2,
                            "items": [
                                {
                                    "id": 10,
                                    "product": {
                                        "id": 15,
                                        "title": "Anti Hair Loss Shampoo",
                                        "slug": "anti-hair-loss-shampoo",
                                        "thumbnail": (
                                            "https://example.com/"
                                            "media/products/"
                                            "shampoo.jpg"
                                        ),
                                        "price": 450000,
                                    },
                                    "created_at": (
                                        "2026-08-16T12:30:00Z"
                                    ),
                                },
                                {
                                    "id": 11,
                                    "product": {
                                        "id": 22,
                                        "title": "Hair Mask",
                                        "slug": "hair-mask",
                                        "thumbnail": (
                                            "https://example.com/"
                                            "media/products/"
                                            "hair-mask.jpg"
                                        ),
                                        "price": 620000,
                                    },
                                    "created_at": (
                                        "2026-08-16T12:35:00Z"
                                    ),
                                },
                            ],
                        },
                        response_only=True,
                    ),
                    OpenApiExample(
                        name="Empty Wishlist",
                        summary="Empty wishlist",
                        value={
                            "count": 0,
                            "items": [],
                        },
                        response_only=True,
                    ),
                ],
            ),
        },
    )
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

    @extend_schema(
        tags=["Wishlist"],
        summary="Toggle Product in Wishlist",
        description=(
            "Add a product to the wishlist if it is not already "
            "present. If the product is already in the wishlist, "
            "remove it instead."
        ),
        request=WishlistToggleSerializer,
        examples=[
            OpenApiExample(
                name="Toggle Product",
                summary="Add or remove a product",
                description=(
                    "Send the product ID. If the product is not "
                    "in the wishlist, it will be added. If it is "
                    "already in the wishlist, it will be removed."
                ),
                value={
                    "product": 15,
                },
                request_only=True,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=WishlistToggleResponseSerializer,
                description="Wishlist updated successfully.",
                examples=[
                    OpenApiExample(
                        name="Product Added",
                        summary="Product added to wishlist",
                        value={
                            "is_favorited": True,
                            "action": "added",
                        },
                        response_only=True,
                    ),
                    OpenApiExample(
                        name="Product Removed",
                        summary="Product removed from wishlist",
                        value={
                            "is_favorited": False,
                            "action": "removed",
                        },
                        response_only=True,
                    ),
                ],
            ),
            400: OpenApiResponse(
                description="Invalid product ID.",
            ),
            404: OpenApiResponse(
                description="Product not found.",
            ),
        },
    )
    def post(self, request):
        serializer = WishlistToggleSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        product = serializer.validated_data["product"]

        wishlist, created = self.get_wishlist()

        result = WishlistService.toggle_product(
            wishlist=wishlist,
            product=product,
        )

        response = Response(
            result,
            status=status.HTTP_200_OK,
        )

        if created and not request.user.is_authenticated:
            self.set_guest_cookie(
                response,
                wishlist,
            )

        return response


class WishlistItemDeleteAPIView(WishlistBaseAPIView):

    @extend_schema(
        tags=["Wishlist"],
        summary="Remove Product from Wishlist",
        description=(
            "Remove a specific product from the current "
            "user's wishlist.\n\n"
            "This endpoint works for both authenticated users "
            "and guests. Guest users are identified using the "
            "`wishlist_token` cookie.\n\n"
            "If the product is successfully removed, the API "
            "returns `is_favorited: false`."
        ),
        parameters=[
            OpenApiParameter(
                name="product_id",
                type=int,
                location=OpenApiParameter.PATH,
                required=True,
                description=(
                    "The ID of the product that should be "
                    "removed from the wishlist."
                ),
                examples=[
                    OpenApiExample(
                        name="Example Product",
                        value=15,
                    ),
                ],
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=WishlistDeleteResponseSerializer,
                description=(
                    "Product successfully removed "
                    "from the wishlist."
                ),
                examples=[
                    OpenApiExample(
                        name="Product Removed",
                        summary="Successful deletion",
                        value={
                            "detail": (
                                "Product removed "
                                "from wishlist."
                            ),
                            "product_id": 15,
                            "is_favorited": False,
                        },
                        response_only=True,
                    ),
                ],
            ),
            404: OpenApiResponse(
                description=(
                    "The specified product is not "
                    "in the wishlist."
                ),
                examples=[
                    OpenApiExample(
                        name="Product Not In Wishlist",
                        value={
                            "detail": (
                                "Product is not "
                                "in wishlist."
                            ),
                        },
                        response_only=True,
                    ),
                ],
            ),
        },
    )
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
                    "detail": (
                        "Product is not in wishlist."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        response = Response(
            {
                "detail": (
                    "Product removed from wishlist."
                ),
                "product_id": product_id,
                "is_favorited": False,
            },
            status=status.HTTP_200_OK,
        )

        if created and not request.user.is_authenticated:
            self.set_guest_cookie(
                response,
                wishlist,
            )

        return response