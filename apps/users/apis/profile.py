from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework import status
from rest_framework import generics

from apps.users.serializers import ProfileSummarySerializer, ProfileSerializer


class ProfileSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSummarySerializer

    def get(self, request):
        serializer = self.serializer_class(
            request.user,
            context={"request": request},
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class ProfileAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user
