from django.db import models
from django.db.models import Prefetch
from django.utils import timezone

from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from apps.products.models import (
    Product,
    ProductVariant,
    ProductImage,
    DiscountCampaign,
)
from apps.products.serializers import (
    DiscountCampaignSerializer,
)


class ActiveDiscountCampaignView(ListAPIView):
    serializer_class = DiscountCampaignSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        now = timezone.now()

        discounted_variants = ProductVariant.objects.filter(
            is_active=True,
            discounted_price__isnull=False,
            discounted_price__lt=models.F("price"),
        )

        primary_images = ProductImage.objects.filter(
            is_primary=True,
        )

        discounted_products = Product.objects.filter(
            is_available=True,
            variants__in=discounted_variants,
        ).distinct()

        return (
            DiscountCampaign.objects
            .filter(
                is_active=True,
                starts_at__lte=now,
                ends_at__gt=now,
                products__in=discounted_products,
            )
            .distinct()
            .prefetch_related(
                Prefetch(
                    "products",
                    queryset=discounted_products.prefetch_related(
                        Prefetch(
                            "variants",
                            queryset=discounted_variants,
                        ),
                        Prefetch(
                            "images",
                            queryset=primary_images,
                        ),
                    ),
                )
            )
        )