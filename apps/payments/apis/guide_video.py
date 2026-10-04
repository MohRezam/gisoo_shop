from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.payments.models import PaymentGuideVideo
from apps.payments.serializers.guide_video import PaymentGuideVideoSerializer
from apps.shared.cache.list_cache import cached_action_response
from apps.shared.cache import namespaces as ns


@extend_schema(
    tags=["Payments"],
    summary="Get card-to-card payment guide video",
    description=(
        "Returns the tutorial video shown in the payment page "
        "«آموزش پرداخت آسان» sheet. Cached."
    ),
    responses={200: PaymentGuideVideoSerializer},
)
class PaymentGuideVideoAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        def builder():
            obj = PaymentGuideVideo.load()
            return PaymentGuideVideoSerializer(obj, context={"request": request}).data

        return cached_action_response(
            ns.PAYMENT_GUIDE_VIDEO,
            request,
            builder,
            ttl=60 * 30,
        )
