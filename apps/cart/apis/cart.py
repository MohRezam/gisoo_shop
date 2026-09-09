from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from apps.cart.serializers import AddCartItemSerializer, CartSerializer, UpdateCartItemSerializer, \
    ApplyDiscountSerializer
from apps.cart.services import get_cart, apply_discount_to_cart, remove_discount_from_cart
from apps.cart.services.cart import add_to_cart, update_cart_item, delete_cart_item
from rest_framework.generics import RetrieveAPIView
from apps.cart.models import Cart
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers


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


class CartDiscountAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=ApplyDiscountSerializer,
        responses={
            200: inline_serializer(
                name="CartDiscountResponse",
                fields={
                    "discount": serializers.CharField(),
                    "original_subtotal": serializers.IntegerField(),
                    "product_discount": serializers.IntegerField(),
                    "subtotal": serializers.IntegerField(),
                    "coupon_discount": serializers.IntegerField(),
                    "total": serializers.IntegerField(),
                },
            ),
        },
    )
    def post(self, request):
        serializer = ApplyDiscountSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        cart_uuid = request.headers.get(
            "X-Cart-UUID"
        )

        cart = get_cart(
            user=request.user,
            cart_uuid=cart_uuid,
        )

        if cart is None:
            return Response(
                {"detail": "Cart not found."},
                status=404,
            )

        result = apply_discount_to_cart(
            cart=cart,
            user=request.user,
            code=serializer.validated_data["code"],
        )

        return Response({
            "discount": result["discount"].code,
            "original_subtotal": result["original_subtotal"],
            "product_discount": result["product_discount"],
            "subtotal": result["subtotal"],
            "coupon_discount": result["coupon_discount"],
            "total": result["total"],
        })

    @extend_schema(
        responses={
            200: inline_serializer(
                name="CartRemoveDiscountResponse",
                fields={
                    "discount": serializers.CharField(
                        allow_null=True
                    ),
                    "original_subtotal": serializers.IntegerField(),
                    "product_discount": serializers.IntegerField(),
                    "subtotal": serializers.IntegerField(),
                    "coupon_discount": serializers.IntegerField(),
                    "total": serializers.IntegerField(),
                },
            ),
        },
    )
    def delete(self, request):
        cart_uuid = request.headers.get(
            "X-Cart-UUID"
        )

        cart = get_cart(
            user=request.user,
            cart_uuid=cart_uuid,
        )

        if cart is None:
            return Response(
                {"detail": "Cart not found."},
                status=404,
            )

        result = remove_discount_from_cart(
            cart=cart,
            user=request.user,
        )

        return Response({
            "discount": None,
            "original_subtotal": result["original_subtotal"],
            "product_discount": result["product_discount"],
            "subtotal": result["subtotal"],
            "coupon_discount": result["coupon_discount"],
            "total": result["total"],
        })
