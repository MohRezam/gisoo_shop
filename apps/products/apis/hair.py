from drf_spectacular.utils import (
    extend_schema,
)
from rest_framework.generics import ListAPIView

from apps.products.models import HairProblem
from apps.products.serializers import HairProblemSerializer
from apps.shared.cache.list_cache import CachedListMixin
from apps.shared.cache import namespaces as ns
from utils.paginators import StandardResultPagination


@extend_schema(
    tags=["Hair Problems"],
    summary="List Hair Problems",
)
class HairProblemAPIView(CachedListMixin, ListAPIView):
    serializer_class = HairProblemSerializer
    queryset = HairProblem.objects.filter(is_active=True)
    filter_backends = []
    pagination_class = StandardResultPagination
    cache_namespace = ns.PRODUCTS_HAIR_PROBLEMS
    cache_ttl = 60 * 30
