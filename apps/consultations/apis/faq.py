from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny

from apps.consultations.models import ConsultationFAQ
from apps.consultations.serializers.faq import ConsultationFAQSerializer
from apps.shared.cache import namespaces as ns
from apps.shared.cache.list_cache import CachedListMixin


@extend_schema(
    tags=["Consultations"],
    summary="Consultation page FAQs",
    description="Active FAQs for the /consult page only (max 6). Cached.",
)
class ConsultationFAQListAPIView(CachedListMixin, generics.ListAPIView):
    serializer_class = ConsultationFAQSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    cache_namespace = ns.CONSULTATIONS_FAQ
    cache_ttl = 60 * 30

    def get_queryset(self):
        return (
            ConsultationFAQ.objects.filter(is_active=True)
            .order_by("ordering", "id")[:6]
        )
