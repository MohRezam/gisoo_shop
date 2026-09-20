from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView

from apps.home.models import HomeAbout
from apps.home.serializers import HomeAboutSerializer
from apps.shared.cache.list_cache import CachedListMixin
from apps.shared.cache import namespaces as ns
from utils.paginators import StandardResultPagination


@extend_schema(
    tags=["Home"],
    summary="Get homepage About Us",
    description="Returns active About Us for the homepage. Cached.",
)
class HomeAboutAPIView(CachedListMixin, ListAPIView):
    serializer_class = HomeAboutSerializer
    pagination_class = StandardResultPagination
    cache_namespace = ns.HOME_ABOUT
    cache_ttl = 60 * 30

    queryset = (
        HomeAbout.objects
        .filter(is_active=True)
        .order_by("display_order", "-created_at")
    )
