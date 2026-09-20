from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from rest_framework import generics

from apps.home.models import FAQCategory, FAQ
from apps.home.serializers.frequently_asked_questions import FAQCategorySerializer
from apps.shared.cache.list_cache import CachedListMixin
from apps.shared.cache import namespaces as ns
from utils.paginators import StandardResultPagination


@extend_schema(
    tags=["Home"],
    summary="Get FAQ List",
    description="Returns active FAQ for the home page. Cached.",
)
class FAQListAPIView(CachedListMixin, generics.ListAPIView):
    serializer_class = FAQCategorySerializer
    pagination_class = StandardResultPagination
    cache_namespace = ns.HOME_FAQ
    cache_ttl = 60 * 30

    def get_queryset(self):
        active_faqs = FAQ.objects.filter(
            is_active=True,
        ).order_by(
            "ordering",
            "id",
        )

        return (
            FAQCategory.objects
            .filter(is_active=True)
            .prefetch_related(
                Prefetch(
                    "faqs",
                    queryset=active_faqs,
                )
            )
            .order_by(
                "ordering",
                "id",
            )
        )
