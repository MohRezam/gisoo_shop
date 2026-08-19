from django.db.models import Min, Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework.filters import (
    OrderingFilter,
    SearchFilter,
)
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
)

from apps.products.filters import ProductFilter
from apps.products.models import (
    Product,
    ProductImage,
    ProductVariant, Bundle, ProductAttribute,
)
from apps.products.serializers import (
    ProductDetailSerializer,
    ProductListSerializer, SpecialOfferProductListSerializer,
)
from utils.paginators import StandardResultPagination
from django.db.models import F


@extend_schema(
    tags=["Products"],
    summary="List Products",
    parameters=[
        OpenApiParameter(
            name="category",
            type=int,
            description="Category ID",
        ),
        OpenApiParameter(
            name="brand",
            type=int,
            description="Brand ID",
        ),
        OpenApiParameter(
            name="min_price",
            type=int,
            description="Minimum price",
        ),
        OpenApiParameter(
            name="max_price",
            type=int,
            description="Maximum price",
        ),
        OpenApiParameter(
            name="search",
            type=str,
            description="Search products",
        ),
        OpenApiParameter(
            name="ordering",
            type=str,
            description="price, -price, created_at, -created_at",
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=ProductListSerializer,
        ),
    },
)
class ProductListAPIView(ListAPIView):
    serializer_class = ProductListSerializer
    pagination_class = StandardResultPagination

    queryset = (
        Product.objects
        .filter(is_available=True)
        .select_related(
            "brand",
            "category",
        )
        .prefetch_related(
            Prefetch(
                "images",
                queryset=ProductImage.objects.filter(
                    is_primary=True,
                ),
                to_attr="primary_images",
            ),
            Prefetch(
                "variants",
                queryset=(
                    ProductVariant.objects
                    .filter(is_active=True)
                    .order_by("price")
                ),
                to_attr="active_variants",
            ),
        )
        .annotate(
            price=Min("variants__price"),
        )
        .distinct()
    )

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = ProductFilter

    search_fields = [
        "title",
        "category__title",
        "brand__title",
        "hair_problems__title",
    ]

    ordering_fields = [
        "price",
        "created_at",
    ]

    ordering = [
        "-created_at",
    ]


@extend_schema(
    tags=["Products"],
    summary="Retrieve Product",
    responses={
        200: ProductDetailSerializer,
    },
)
class ProductDetailAPIView(RetrieveAPIView):
    serializer_class = ProductDetailSerializer

    queryset = (
        Product.objects
        .filter(
            is_available=True,
        )
        .select_related(
            "brand",
            "category",
        )
        .prefetch_related(

            Prefetch(
                "images",
                queryset=ProductImage.objects.order_by(
                    "-is_primary",
                    "created_at",
                ),
            ),

            Prefetch(
                "variants",
                queryset=(
                    ProductVariant.objects
                    .filter(
                        is_active=True,
                    )
                    .prefetch_related(
                        "attributes__value__attribute",
                    )
                    .order_by(
                        "created_at",
                    )
                ),
            ),

            Prefetch(
                "product_attributes",
                queryset=(
                    ProductAttribute.objects
                    .select_related("attribute")
                    .order_by(
                        "display_order",
                        "created_at",
                    )
                ),
            ),

            Prefetch(
                "bundles",
                queryset=(
                    Bundle.objects
                    .filter(
                        is_active=True,
                    )
                    .prefetch_related(
                        "items__variant__attributes__value__attribute",
                    )
                    .order_by(
                        "display_order",
                        "created_at",
                    )
                ),
            ),

            # Manual related products selected by admin
            Prefetch(
                "related_products",
                queryset=(
                    Product.objects
                    .filter(
                        is_available=True,
                    )
                    .prefetch_related(
                        "images",
                        "variants",
                    )
                    .order_by(
                        "related_product_relations__display_order",
                        "-created_at",
                    )
                ),
                to_attr="manual_related_products",
            ),
        )
    )

    lookup_field = "slug"


@extend_schema(
    tags=["Products"],
    summary="Special Offer Product List",
    responses={
        200: ProductDetailSerializer,
    },
)
class SpecialOfferProductListAPIView(ListAPIView):
    serializer_class = SpecialOfferProductListSerializer
    pagination_class = StandardResultPagination

    def get_queryset(self):
        return (
            Product.objects
            .filter(
                is_available=True,
                variants__is_active=True,
                variants__stock__gt=0,
                variants__discounted_price__isnull=False,
                variants__discounted_price__lt=F(
                    "variants__price",
                ),
            )
            .select_related(
                "brand",
                "category",
            )
            .prefetch_related(
                Prefetch(
                    "images",
                    queryset=ProductImage.objects.filter(
                        is_primary=True,
                    ),
                    to_attr="primary_images",
                ),
                Prefetch(
                    "variants",
                    queryset=(
                        ProductVariant.objects
                        .filter(
                            is_active=True,
                            stock__gt=0,
                            discounted_price__isnull=False,
                            discounted_price__lt=F("price"),
                        )
                        .order_by("discounted_price")
                    ),
                    to_attr="active_variants",
                ),
            )
            .distinct()
            .order_by("-created_at")
        )
