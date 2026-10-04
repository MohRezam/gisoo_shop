from django.utils import timezone

from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from apps.products.models import DiscountCampaign
from apps.products.serializers import (
    DiscountCampaignSerializer,
)
from apps.products.services.discount_campaign import (
    campaign_member_products_queryset,
)


class ActiveDiscountCampaignView(ListAPIView):
    serializer_class = DiscountCampaignSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        now = timezone.now()

        return (
            DiscountCampaign.objects
            .filter(
                is_active=True,
                starts_at__lte=now,
                ends_at__gt=now,
            )
            .order_by("-created_at")
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["campaign_products"] = list(
            campaign_member_products_queryset()
        )
        return context
