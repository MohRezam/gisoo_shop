from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView

from apps.home.models import HomeAbout
from apps.home.serializers import HomeAboutSerializer
from utils.paginators import StandardResultPagination


@extend_schema(
    tags=["Home"],
    summary="Get homepage About Us",
    description="Returns active About Us for the homepage.",
)
class HomeAboutAPIView(ListAPIView):
    serializer_class = HomeAboutSerializer
    pagination_class = StandardResultPagination

    queryset = (
        HomeAbout.objects
        .filter(is_active=True)
        .order_by("display_order", "-created_at")
    )
