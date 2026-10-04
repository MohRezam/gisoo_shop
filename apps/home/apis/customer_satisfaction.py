from drf_spectacular.utils import extend_schema
from rest_framework import generics

from apps.home.models import CustomerSatisfaction
from apps.home.serializers import CustomerSatisfactionSerializer
from apps.shared.cache.list_cache import CachedListMixin
from apps.shared.cache import namespaces as ns
from utils.paginators import StandardResultPagination


@extend_schema(
    tags=["Home"],
    summary="Get Customers Satisfactions",
    description="Returns Active Customers Satisfed. Cached.",
)
class CustomerSatisfactionListAPIView(CachedListMixin, generics.ListAPIView):
    serializer_class = CustomerSatisfactionSerializer
    pagination_class = StandardResultPagination
    cache_namespace = ns.HOME_SATISFACTION
    cache_ttl = 60 * 15

    def get_queryset(self):
        return CustomerSatisfaction.objects.filter(
            is_active=True
        )
