from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.generics import ListAPIView

from apps.home.models import HomeAbout
from apps.home.serializers import HomeAboutSerializer
from apps.shared.cache.list_cache import CachedListMixin
from apps.shared.cache import namespaces as ns
from utils.paginators import StandardResultPagination


@extend_schema(
    tags=["Home"],
    summary="Get About Us sections",
    description=(
        "Returns active About Us blocks. "
        "section=intro is used on the homepage and as the first about-page block; "
        "section=story and section=cta are the second and third about-page blocks. "
        "Optional filter: ?section=intro|story|cta. Cached."
    ),
    parameters=[
        OpenApiParameter(
            name="section",
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            enum=["intro", "story", "cta"],
            description="Filter by about section key.",
        ),
    ],
)
class HomeAboutAPIView(CachedListMixin, ListAPIView):
    serializer_class = HomeAboutSerializer
    pagination_class = StandardResultPagination
    cache_namespace = ns.HOME_ABOUT
    cache_ttl = 60 * 30

    def get_queryset(self):
        qs = (
            HomeAbout.objects
            .filter(is_active=True)
            .order_by("display_order", "-created_at")
        )
        section = self.request.query_params.get("section")
        if section in {"intro", "story", "cta"}:
            qs = qs.filter(section=section)
        return qs
