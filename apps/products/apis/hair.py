from django.db.models import Max, Min
from django.db.models.functions import Coalesce
from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView

from apps.products.models import HairProblem, HairType, ProductVariant
from apps.products.serializers import HairProblemSerializer, HairTypeSerializer
from apps.shared.cache.list_cache import CachedListMixin, cached_action_response
from apps.shared.cache import namespaces as ns
from utils.paginators import StandardResultPagination


# Storefront sort chips — `ordering` is the query value for ProductListAPIView.
PRODUCT_SORT_OPTIONS = [
    {
        "id": "suggested",
        "label": "پیشنهادی گیسو سنتر",
        "ordering": "",
    },
    {
        "id": "bestsellers",
        "label": "پرفروش‌ترین",
        "ordering": "-id",
    },
    {
        "id": "newest",
        "label": "جدیدترین",
        "ordering": "-created_at",
    },
    {
        "id": "price-asc",
        "label": "ارزان‌ترین",
        "ordering": "price",
    },
    {
        "id": "price-desc",
        "label": "گران‌ترین",
        "ordering": "-price",
    },
    {
        "id": "discount",
        "label": "بیشترین تخفیف",
        "ordering": "-discount_amount",
    },
]

# Fixed toman presets for the shop filter (matches storefront UX).
PRODUCT_PRICE_PRESETS = [
    {
        "id": "under-500",
        "label": "تا ۵۰۰ هزار",
        "min_price": 0,
        "max_price": 500_000,
    },
    {
        "id": "500-1m",
        "label": "۵۰۰ هزار تا ۱ میلیون",
        "min_price": 500_000,
        "max_price": 1_000_000,
    },
    {
        "id": "1m-2m",
        "label": "۱ تا ۲ میلیون",
        "min_price": 1_000_000,
        "max_price": 2_000_000,
    },
    {
        "id": "over-2m",
        "label": "بالای ۲ میلیون",
        "min_price": 2_000_000,
        "max_price": None,
    },
]


@extend_schema(
    tags=["Hair Problems"],
    summary="List Hair Problems",
)
class HairProblemAPIView(CachedListMixin, ListAPIView):
    serializer_class = HairProblemSerializer
    queryset = HairProblem.objects.filter(is_active=True)
    filter_backends = []
    pagination_class = StandardResultPagination
    cache_namespace = ns.PRODUCTS_HAIR_PROBLEMS
    cache_ttl = 60 * 30


@extend_schema(
    tags=["Hair Types"],
    summary="List Hair Types",
)
class HairTypeAPIView(CachedListMixin, ListAPIView):
    serializer_class = HairTypeSerializer
    queryset = HairType.objects.filter(is_active=True)
    filter_backends = []
    pagination_class = StandardResultPagination
    cache_namespace = ns.PRODUCTS_HAIR_TYPES
    cache_ttl = 60 * 30


def _catalog_price_bounds():
    """Min/max of active variant list prices among available products."""
    qs = ProductVariant.objects.filter(
        is_active=True,
        product__is_available=True,
    )
    agg = qs.aggregate(
        min_price=Min("price"),
        max_price=Max("price"),
        min_sale=Min(Coalesce("discounted_price", "price")),
        max_sale=Max(Coalesce("discounted_price", "price")),
    )
    low = agg["min_sale"] if agg["min_sale"] is not None else agg["min_price"]
    high = agg["max_price"] if agg["max_price"] is not None else agg["max_sale"]
    if low is None:
        low = 0
    if high is None:
        high = 0
    return {"min": int(low), "max": int(high)}


@extend_schema(
    tags=["Products"],
    summary="Shop filter metadata",
    description=(
        "Price bounds/presets and sort options for the storefront filter panel. "
        "Hair types are also listed at /api/products/v1/hair/types/."
    ),
)
class ProductFiltersMetaAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        def builder():
            hair_types = HairTypeSerializer(
                HairType.objects.filter(is_active=True),
                many=True,
                context={"request": request},
            ).data
            return {
                "price": _catalog_price_bounds(),
                "price_presets": PRODUCT_PRICE_PRESETS,
                "sort_options": PRODUCT_SORT_OPTIONS,
                "hair_types": hair_types,
            }

        return cached_action_response(
            ns.PRODUCTS_FILTERS_META,
            request,
            builder,
            ttl=60 * 30,
        )
