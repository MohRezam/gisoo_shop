from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from apps.consultations.models import ConsultationPageBlock
from apps.consultations.serializers.page_content import (
    ConsultationPageBlockSerializer,
)
from apps.shared.cache import namespaces as ns
from apps.shared.cache.list_cache import CachedListMixin
from utils.paginators import StandardResultPagination


@extend_schema(
    tags=["Consultations"],
    summary="Consultation page content blocks",
    description=(
        "Returns active intro/cta blocks (title, text, image) for /consult. Cached."
    ),
)
class ConsultationPageContentAPIView(CachedListMixin, ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ConsultationPageBlockSerializer
    pagination_class = StandardResultPagination
    cache_namespace = ns.CONSULTATIONS_PAGE
    cache_ttl = 60 * 30

    queryset = (
        ConsultationPageBlock.objects
        .filter(is_active=True)
        .order_by("section")
    )
