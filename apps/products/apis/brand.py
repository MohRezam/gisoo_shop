from drf_spectacular.utils import (
    extend_schema,
)
from rest_framework.generics import ListAPIView

from apps.products.models import Brand
from apps.products.serializers import BrandSerializer


@extend_schema(
    tags=["Products"],
    summary="List Brands",
)
class BrandListAPIView(ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    filter_backends = []