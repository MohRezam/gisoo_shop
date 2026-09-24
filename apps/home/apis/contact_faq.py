from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny

from apps.home.models import ContactFAQ
from apps.home.serializers.contact_faq import ContactFAQSerializer
from apps.shared.cache import namespaces as ns
from apps.shared.cache.list_cache import CachedListMixin


@extend_schema(
    tags=["Home"],
    summary="Contact page FAQs",
    description="Active FAQs for the /contact page only (max 6). Cached.",
)
class ContactFAQListAPIView(CachedListMixin, generics.ListAPIView):
    serializer_class = ContactFAQSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    cache_namespace = ns.HOME_CONTACT_FAQ
    cache_ttl = 60 * 30

    def get_queryset(self):
        return (
            ContactFAQ.objects.filter(is_active=True)
            .order_by("ordering", "id")[:6]
        )
