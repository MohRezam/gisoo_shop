from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.products.models import Product
from apps.products.models.stock_notify import WishlistStockNotify


class WishlistStockNotifySerializer(serializers.Serializer):
    product_id = serializers.IntegerField()


@extend_schema(
    tags=["Wishlist"],
    summary="Notify when product is back in stock",
    description=(
        "Registers the authenticated user to receive an in-app notification "
        "(`type=stock`) when the product stock becomes available again.\n\n"
        "Body uses numeric `product_id` (not slug)."
    ),
    request=WishlistStockNotifySerializer,
    responses={
        201: OpenApiResponse(
            examples=[
                OpenApiExample(
                    "OK",
                    value={
                        "product_id": 15,
                        "subscribed": True,
                        "message": "You will be notified when this product is back in stock.",
                    },
                )
            ]
        ),
        404: OpenApiResponse(description="Product not found."),
    },
)
class WishlistStockNotifyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = WishlistStockNotifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_id = serializer.validated_data["product_id"]

        product = Product.objects.filter(pk=product_id).first()
        if product is None:
            return Response(
                {"detail": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        obj, created = WishlistStockNotify.objects.update_or_create(
            user=request.user,
            product=product,
            defaults={"is_notified": False, "notified_at": None},
        )
        return Response(
            {
                "product_id": product.id,
                "subscribed": True,
                "created": created,
                "message": "You will be notified when this product is back in stock.",
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
