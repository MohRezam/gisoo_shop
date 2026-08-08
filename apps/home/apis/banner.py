from apps.home.models import Banner
from apps.home.serializers.banner import BannerSerializer

from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView

from utils.paginators import StandardResultPagination


@extend_schema(
    tags=["Home"],
    summary="Get homepage hero banners",
    description="Returns active hero banners for the homepage.",
)
class BannerAPIView(ListAPIView):
    serializer_class = BannerSerializer
    pagination_class = StandardResultPagination

    queryset = (
        Banner.objects
        .filter(is_active=True)
        .select_related("product", "category")
        .order_by("display_order", "-created_at")
    )
