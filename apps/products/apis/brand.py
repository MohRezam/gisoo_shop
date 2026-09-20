from drf_spectacular.utils import (
    extend_schema,
)
from rest_framework.generics import ListAPIView

from apps.products.models import Brand
from apps.products.serializers import BrandSerializer
from apps.shared.cache.list_cache import CachedListMixin
from apps.shared.cache import namespaces as ns


@extend_schema(
    tags=["Products"],
    summary="List Brands",
)
class BrandListAPIView(CachedListMixin, ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    filter_backends = []
    cache_namespace = ns.PRODUCTS_BRANDS
    cache_ttl = 60 * 30
