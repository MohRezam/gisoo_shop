from rest_framework.exceptions import APIException
from rest_framework import status


class CartItemNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    default_detail = "Cart item not found."

    default_code = "cart_item_not_found"
