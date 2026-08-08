from rest_framework.generics import ListAPIView

from apps.products.models import Banner
from apps.products.serializers.banner import BannerSerializer


class BannerAPIView(ListAPIView):
    serializer_class = BannerSerializer
    pagination_class = None

    queryset = (
        Banner.objects
        .filter(is_active=True)
        .select_related("product", "category")
        .order_by("display_order", "-created_at")
    )