from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView


class GetStorage(APIView):
    def post(self, request, *args, **kwargs):
        storage_data = {
            "AWS_ACCESS_KEY_ID": settings.AWS_ACCESS_KEY_ID,
            "AWS_SECRET_ACCESS_KEY": settings.AWS_SECRET_ACCESS_KEY,
            "AWS_STORAGE_BUCKET_NAME": "index-public",
            "AWS_S3_HOST": settings.AWS_S3_HOST,
            "AWS_S3_ENDPOINT_URL": settings.AWS_S3_ENDPOINT_URL,
        }
        return Response(data=storage_data)
