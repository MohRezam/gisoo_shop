from django.db.models import (
    Avg,
    Count,
    Min,
    OuterRef,
    Prefetch,
    Q,
    Subquery,
    Sum,
    Value,
)
from django.db.models.functions import Coalesce
from django.db.models import IntegerField
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

from apps.orders.models import OrderItem, OrderStatus
from apps.products.filters import ProductFilter
from apps.products.models import (
    Product,
    ProductFAQ,
    ProductImage,
    ProductVariant, Bundle, ProductAttribute, ProductRelatedProduct,
)
from apps.products.serializers import (
    ProductDetailSerializer,
    ProductListSerializer, SpecialOfferProductListSerializer, RelatedProductSerializer,
)
from apps.reviews.models import ProductReview, ReviewStatus
from apps.shared.cache.list_cache import CachedListMixin, CachedRetrieveMixin
from apps.shared.cache import namespaces as ns
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

_SOLD_ORDER_STATUSES = (
    OrderStatus.PREPARING,
    OrderStatus.SHIPPED,
    OrderStatus.DELIVERED,
)

_SOLD_COUNT_SUBQUERY = (
    OrderItem.objects.filter(
        variant__product_id=OuterRef("pk"),
        order__status__in=_SOLD_ORDER_STATUSES,
    )
    .values("variant__product_id")
    .annotate(total=Sum("quantity"))
    .values("total")[:1]
)


def _base_product_list_queryset():
    """Shared annotations for catalog list — sold_count added only when needed."""
    return (
        Product.objects
        .filter(is_available=True)
        .select_related(
            "brand",
        )
        .prefetch_related(
            "categories",
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
                    .order_by("display_order", "price")
                ),
                to_attr="active_variants",
            ),
        )
        .annotate(
            price=Min("variants__price"),
            discounted_price=Min(
                Coalesce(
                    "variants__discounted_price",
                    "variants__price",
                )
            ),
        )
        .annotate(
            discount_amount=F("price") - F("discounted_price"),
        )
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
            description="Minimum variant list price (toman)",
        ),
        OpenApiParameter(
            name="max_price",
            type=int,
            description="Maximum variant list price (toman)",
        ),
        OpenApiParameter(
            name="hair_problem",
            type=str,
            description="Hair problem ID, or comma-separated IDs",
        ),
        OpenApiParameter(
            name="hair_type",
            type=str,
            description="Hair type ID, or comma-separated IDs",
        ),
        OpenApiParameter(
            name="search",
            type=str,
            description="Search products",
        ),
        OpenApiParameter(
            name="ordering",
            type=str,
            description=(
                "price, -price, created_at, -created_at, "
                "discounted_price, -discounted_price, "
                "discount_amount, -discount_amount, id, -id, "
                "sold_count, -sold_count, "
                "is_gisoo_recommended, -is_gisoo_recommended, "
                "recommended_order, -recommended_order "
                "(comma-separated multi-field ok)"
            ),
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=ProductListSerializer,
        ),
    },
)
class ProductListAPIView(CachedListMixin, ListAPIView):
    serializer_class = ProductListSerializer
    pagination_class = StandardResultPagination
    cache_namespace = ns.PRODUCTS_LIST
    cache_ttl = 60 * 5

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = ProductFilter

    search_fields = [
        "title",
        "categories__title",
        "brand__title",
        "hair_problems__title",
        "hair_types__title",
    ]

    ordering_fields = [
        "price",
        "discounted_price",
        "discount_amount",
        "created_at",
        "id",
        "sold_count",
        "is_gisoo_recommended",
        "recommended_order",
    ]

    ordering = [
        "-is_gisoo_recommended",
        "recommended_order",
        "-created_at",
    ]

    def get_queryset(self):
        qs = _base_product_list_queryset()
        ordering = self.request.query_params.get("ordering") or ""
        # Heavy sales subquery only when sorting by bestsellers.
        if "sold_count" in ordering:
            qs = qs.annotate(
                sold_count=Coalesce(
                    Subquery(
                        _SOLD_COUNT_SUBQUERY,
                        output_field=IntegerField(),
                    ),
                    Value(0),
                    output_field=IntegerField(),
                ),
            )
        return qs.distinct()


@extend_schema(
    tags=["Products"],
    summary="Retrieve Product",
    responses={
        200: ProductDetailSerializer,
    },
)
class ProductDetailAPIView(CachedRetrieveMixin, RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    cache_namespace = ns.PRODUCTS_DETAIL
    cache_ttl = 60 * 10
    cache_lookup_kwarg = "slug"
    lookup_field = "slug"

    queryset = (
        Product.objects
        .filter(
            is_available=True,
        )
        .select_related(
            "brand",
        )
        .prefetch_related(
            "categories",
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
                        "display_order",
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

            Prefetch(
                "reviews",
                queryset=(
                    ProductReview.objects
                    .filter(
                        status=ReviewStatus.APPROVED,
                    )
                    .select_related(
                        "user",
                    )
                    .order_by(
                        "-created_at",
                    )[:5]
                ),
                to_attr="approved_reviews",
            ),

            Prefetch(
                "faqs",
                queryset=(
                    ProductFAQ.objects
                    .filter(is_active=True)
                    .order_by("ordering", "id")[:6]
                ),
                to_attr="active_faqs",
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
        .annotate(
            reviews_count=Count(
                "reviews",
                filter=Q(
                    reviews__status="approved",
                ),
            ),
            reviews_average=Avg(
                "reviews__rating",
                filter=Q(
                    reviews__status="approved",
                ),
            ),
            reviews_5=Count(
                "reviews",
                filter=Q(
                    reviews__status="approved",
                    reviews__rating=5,
                ),
            ),
            reviews_4=Count(
                "reviews",
                filter=Q(
                    reviews__status="approved",
                    reviews__rating=4,
                ),
            ),
            reviews_3=Count(
                "reviews",
                filter=Q(
                    reviews__status="approved",
                    reviews__rating=3,
                ),
            ),
            reviews_2=Count(
                "reviews",
                filter=Q(
                    reviews__status="approved",
                    reviews__rating=2,
                ),
            ),
            reviews_1=Count(
                "reviews",
                filter=Q(
                    reviews__status="approved",
                    reviews__rating=1,
                ),
            ),
        )
    )


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
            .prefetch_related(
                "categories",
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

        category_ids = list(
            product.categories.values_list("id", flat=True)
        )
        if not category_ids:
            return Product.objects.none()

        # Automatic fallback
        return (
            Product.objects
            .filter(
                categories__in=category_ids,
                is_available=True,
            )
            .exclude(
                pk=product.pk,
            )
            .prefetch_related(
                "images",
                "variants",
            )
            .distinct()
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
class SpecialOfferProductListAPIView(CachedListMixin, ListAPIView):
    serializer_class = SpecialOfferProductListSerializer
    pagination_class = StandardResultPagination
    cache_namespace = ns.PRODUCTS_SPECIAL
    cache_ttl = 60 * 5

    def get_queryset(self):
        from apps.products.services.discount_campaign import (
            special_offer_products_queryset,
        )

        return special_offer_products_queryset()


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
