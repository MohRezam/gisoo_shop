from django.db.models import F, Prefetch, Q
from django.core.cache import cache
import hashlib
import json

from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.products.models import Product, ProductImage, ProductVariant
from apps.products.serializers.product import (
    ProductListSerializer,
    SpecialOfferProductListSerializer,
)
from apps.shared.cache.list_cache import get_cache_version
from apps.shared.cache import namespaces as ns


class ConsultationRequestSerializer(serializers.Serializer):
    hair_problem_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=list,
    )
    hair_type_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=list,
    )
    limit = serializers.IntegerField(required=False, default=12, min_value=1, max_value=50)


@extend_schema(
    tags=["Consultation"],
    summary="Product recommendations for hair consultation",
    description=(
        "Returns recommended products based on selected hair problems and/or hair types.\n\n"
        "Stable payload: `{ count, products }` — `products` uses the shop list card shape."
    ),
    request=ConsultationRequestSerializer,
    responses={
        200: OpenApiResponse(
            examples=[
                OpenApiExample(
                    "Recommendations",
                    value={
                        "count": 1,
                        "products": [
                            {
                                "id": 15,
                                "title": "شامپو ضد ریزش",
                                "slug": "anti-hair-loss-shampoo",
                            }
                        ],
                    },
                )
            ]
        )
    },
)
class ConsultationRecommendationsAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ConsultationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        limit = data["limit"]

        version = get_cache_version(ns.PRODUCTS_CONSULTATION)
        body_key = hashlib.md5(
            json.dumps(
                {
                    "hp": sorted(data["hair_problem_ids"]),
                    "ht": sorted(data["hair_type_ids"]),
                    "limit": limit,
                },
                sort_keys=True,
            ).encode()
        ).hexdigest()[:16]
        cache_key = f"{ns.PRODUCTS_CONSULTATION}:v{version}:{body_key}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        qs = Product.objects.filter(is_available=True).distinct()
        filters = Q()
        if data["hair_problem_ids"]:
            filters |= Q(hair_problems__id__in=data["hair_problem_ids"])
        if data["hair_type_ids"]:
            filters |= Q(hair_types__id__in=data["hair_type_ids"])
        if filters:
            qs = qs.filter(filters)

        qs = qs.prefetch_related(
            "images",
            Prefetch(
                "variants",
                queryset=ProductVariant.objects.filter(is_active=True),
            ),
        ).order_by("-id")[:limit]

        products = ProductListSerializer(
            qs,
            many=True,
            context={"request": request},
        ).data
        payload = {"count": len(products), "products": products}
        cache.set(cache_key, payload, 60 * 5)
        return Response(payload)


@extend_schema(
    tags=["Products"],
    summary="Discount campaigns (deprecated)",
    description=(
        "**Deprecated.** Prefer `GET /api/products/v1/special/offers/`.\n"
        "This endpoint returns the same special-offer products wrapped with a deprecation notice."
    ),
    responses={200: OpenApiResponse(description="Deprecated wrapper around special offers.")},
    deprecated=True,
)
class DiscountCampaignsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        version = get_cache_version(ns.PRODUCTS_SPECIAL)
        key = f"{ns.PRODUCTS_SPECIAL}:campaigns:v{version}"
        cached = cache.get(key)
        if cached is not None:
            return Response(cached)

        qs = list(
            Product.objects.filter(
                is_available=True,
                variants__is_active=True,
                variants__stock__gt=0,
                variants__discounted_price__isnull=False,
                variants__discounted_price__lt=F("variants__price"),
            )
            .select_related("brand", "category")
            .prefetch_related(
                Prefetch(
                    "images",
                    queryset=ProductImage.objects.filter(is_primary=True),
                    to_attr="primary_images",
                ),
                Prefetch(
                    "variants",
                    queryset=ProductVariant.objects.filter(
                        is_active=True,
                        stock__gt=0,
                        discounted_price__isnull=False,
                        discounted_price__lt=F("price"),
                    ),
                ),
            )
            .distinct()
            .order_by("-id")[:50]
        )
        results = SpecialOfferProductListSerializer(
            qs,
            many=True,
            context={"request": request},
        ).data
        payload = {
            "deprecated": True,
            "use": "/api/products/v1/special/offers/",
            "count": len(results),
            "results": results,
        }
        cache.set(key, payload, 60 * 5)
        return Response(payload)
