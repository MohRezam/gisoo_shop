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
    Brand,
    Category,
    Product,
    ProductImage,
    ProductVariant, Bundle, HairProblem,
)
from apps.products.serializers import (
    BrandSerializer,
    CategorySerializer,
    ProductDetailSerializer,
    ProductListSerializer, HairProblemSerializer,
)


@extend_schema(
    tags=["Products"],
    summary="List Categories",
)
class CategoryListAPIView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = []



@extend_schema(
    tags=["Products"],
    summary="List Brands",
)
class BrandListAPIView(ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    filter_backends = []


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
        .filter(is_available=True)
        .select_related(
            "brand",
            "category",
        )
        .prefetch_related(
            "images",
            "variants__attributes__value__attribute",
            Prefetch(
                "bundles",
                queryset=(
                    Bundle.objects
                    .filter(is_active=True)
                    .prefetch_related(
                        "items__variant__product",
                    )
                    .order_by(
                        "display_order",
                    )
                ),
            ),
        )
    )

    lookup_field = "slug"


@extend_schema(
    tags=["Hair Problems"],
    summary="List Hair Problems",
)
class HairProblemAPIView(ListAPIView):
    serializer_class = HairProblemSerializer
    queryset = HairProblem.objects.filter(is_active=True)
    filter_backends = []
    pagination_class = None