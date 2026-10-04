from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.serializers.logout import BlacklistRefreshSerializer


class BlacklistRefreshAPIView(APIView):
    """Blacklist the refresh token on logout.

    Access tokens cannot be blacklisted by simplejwt (only refresh tokens
    are tracked). Keep ACCESS_TOKEN_LIFETIME short so leftover access
    tokens expire quickly after logout.
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
                        "message": (
                            "Refresh token has been successfully blacklisted "
                            "and is no longer valid."
                        )
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
