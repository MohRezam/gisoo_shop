from django.db.models import Min, Prefetch, Subquery, OuterRef
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
    ProductVariant, Bundle, ProductAttribute, ProductRelatedProduct,
)
from apps.products.serializers import (
    ProductDetailSerializer,
    ProductListSerializer, SpecialOfferProductListSerializer, RelatedProductSerializer,
)
from utils.paginators import StandardResultPagination
from django.db.models import F
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.products.services.product_viewers import (
    register_viewer,
    VIEWER_COOKIE_NAME,
)


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

                        Prefetch(
                            "bundles",
                            queryset=(
                                Bundle.objects
                                .filter(
                                    is_active=True,
                                )
                                .order_by(
                                    "display_order",
                                    "created_at",
                                )
                            ),
                        ),
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
                    .select_related(
                        "attribute",
                    )
                    .order_by(
                        "display_order",
                        "created_at",
                    )
                ),
            ),

            # Related products
            Prefetch(
                "related_product_relations",
                queryset=(
                    ProductRelatedProduct.objects
                    .filter(
                        related_product__is_available=True,
                    )
                    .select_related(
                        "related_product",
                    )
                    .order_by(
                        "display_order",
                        "created_at",
                    )
                ),
                to_attr="ordered_related_product_relations",
            ),
        )
    )

    lookup_field = "slug"


@extend_schema(
    tags=["Products"],
    summary="List All Related Products",
    responses={
        200: RelatedProductSerializer(many=True),
    },
)
class ProductRelatedProductsAPIView(ListAPIView):
    serializer_class = RelatedProductSerializer
    pagination_class = StandardResultPagination

    def get_queryset(self):
        product = (
            Product.objects
            .filter(
                slug=self.kwargs["slug"],
                is_available=True,
            )
            .select_related(
                "category",
            )
            .first()
        )

        if not product:
            return Product.objects.none()

        # Manually selected related products
        manual_products = (
            Product.objects
            .filter(
                related_to_relations__product=product,
                is_available=True,
            )
            .exclude(
                pk=product.pk,
            )
            .annotate(
                related_display_order=Subquery(
                    ProductRelatedProduct.objects
                    .filter(
                        product=product,
                        related_product=OuterRef("pk"),
                    )
                    .values(
                        "display_order",
                    )[:1]
                ),
            )
            .prefetch_related(
                "images",
                "variants",
            )
            .order_by(
                "related_display_order",
                "-created_at",
            )
        )

        if manual_products.exists():
            return manual_products

        # Automatic fallback
        return (
            Product.objects
            .filter(
                category=product.category,
                is_available=True,
            )
            .exclude(
                pk=product.pk,
            )
            .prefetch_related(
                "images",
                "variants",
            )
            .order_by(
                "-created_at",
            )
        )


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


@extend_schema(
    tags=["Products"],
    summary="Register product viewer",
    description=(
            "Registers the current user or guest as an active viewer of the product "
            "and returns the number of users currently viewing the product. "
            "The viewer remains active as long as heartbeat requests are sent "
            "within the viewer timeout period."
    ),
    responses={
        200: OpenApiResponse(
            description="Viewer registered successfully.",
            response={
                "type": "object",
                "properties": {
                    "viewers_count": {
                        "type": "integer",
                        "description": "Number of active viewers currently viewing the product.",
                        "example": 7,
                    },
                },
                "required": ["viewers_count"],
            },
        ),
        404: OpenApiResponse(
            description="Product not found or unavailable."
        ),
    },
)
class ProductViewerAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, slug):
        product = (
            Product.objects
            .filter(
                slug=slug,
                is_available=True,
            )
            .only("id")
            .first()
        )

        if not product:
            return Response(
                {
                    "detail": "Product not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        viewers_count, viewer_id = register_viewer(
            request=request,
            product_id=product.id,
        )

        response = Response(
            {
                "viewers_count": viewers_count,
            },
            status=status.HTTP_200_OK,
        )

        if not request.COOKIES.get(
                VIEWER_COOKIE_NAME
        ):
            response.set_cookie(
                key=VIEWER_COOKIE_NAME,
                value=viewer_id.replace(
                    "guest:",
                    "",
                ),
                max_age=60 * 60 * 24 * 365,
                httponly=True,
                samesite="Lax",
            )

        return response
