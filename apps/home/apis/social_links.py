from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView

from apps.home.models import SocialLinks
from apps.home.serializers.social_links import SocialLinksSerializer
from apps.shared.cache.list_cache import cached_action_response
from apps.shared.cache import namespaces as ns


@extend_schema(
    tags=["Home"],
    summary="Get social / messaging links",
    description=(
        "Returns Telegram, Instagram, WhatsApp and Bale URLs "
        "configured in the admin panel. Cached."
    ),
    responses={200: SocialLinksSerializer},
)
class SocialLinksAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        def builder():
            obj = SocialLinks.load()
            return SocialLinksSerializer(obj).data

        return cached_action_response(
            ns.HOME_SOCIAL_LINKS,
            request,
            builder,
            ttl=60 * 30,
        )
