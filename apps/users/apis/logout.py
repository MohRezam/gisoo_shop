from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.serializers.logout import BlacklistRefreshSerializer


class BlacklistRefreshAPIView(APIView):
    """
    Blacklists a refresh token, invalidating it for future use.

    This endpoint accepts a refresh token and blacklists it, preventing it from being used
    in future token refresh requests. If the provided token is invalid or an error occurs,
    a failure message is returned.

    Request:
        - refresh (str): The refresh token to be blacklisted.

    Response:
        - Success message confirming the token has been blacklisted.
        - Error message if the token is invalid or an issue occurs during blacklisting.
    """

    serializer_class = BlacklistRefreshSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                token = RefreshToken(serializer.validated_data["refresh"])
                token.blacklist()
                return Response(
                    {
                        "message": "Refresh token has been successfully blacklisted and is no longer valid."
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception:
                raise ValidationError(
                    _(
                        "Failed to blacklist token. Please ensure the token is valid and try again."
                    )
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
