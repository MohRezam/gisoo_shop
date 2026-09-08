from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from apps.cart.serializers import AddCartItemSerializer, CartSerializer, UpdateCartItemSerializer
from apps.cart.services.cart import add_to_cart, update_cart_item, delete_cart_item
from rest_framework.generics import RetrieveAPIView
from apps.cart.models import Cart
from drf_spectacular.utils import extend_schema


class AddToCartAPIView(APIView):

    @extend_schema(
        request=AddCartItemSerializer,
    )
    def post(self, request):
        serializer = AddCartItemSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        cart_uuid = request.headers.get(
            "X-Cart-UUID"
        )

        cart = add_to_cart(
            cart_uuid=cart_uuid,
            user=request.user,
            variant_id=serializer.validated_data.get(
                "variant_id"
            ),
            bundle_id=serializer.validated_data.get(
                "bundle_id"
            ),
            quantity=serializer.validated_data["quantity"],
        )

        return Response(
            {
                "cart_uuid": str(cart.uuid)
            },
            status=status.HTTP_200_OK,
        )


class CartDetailAPIView(RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [AllowAny]
    lookup_field = "uuid"

    queryset = Cart.objects.prefetch_related(
        "items__variant__product",
        "items__bundle__variant__product",
    )


class UpdateCartItemAPIView(APIView):

    def patch(self, request, item_id):
        serializer = UpdateCartItemSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        update_cart_item(
            user=request.user,
            cart_uuid=request.headers.get(
                "X-Cart-UUID",
            ),
            item_id=item_id,
            quantity=serializer.validated_data[
                "quantity"
            ],
        )

        return Response(
            {
                "detail": "Cart updated."
            },
            status=status.HTTP_200_OK,
        )


class DeleteCartItemAPIView(APIView):

    def delete(self, request, item_id):
        delete_cart_item(
            user=request.user,
            cart_uuid=request.headers.get(
                "X-Cart-UUID",
            ),
            item_id=item_id,
        )

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
