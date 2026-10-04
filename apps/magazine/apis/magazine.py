from django.db.models import Prefetch, Q

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.magazine.models import (
    Magazine,
    MagazineCategory,
)
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from apps.magazine.serializers import (
    MagazineArchiveResponseSerializer,
    MagazineCategorySerializer,
    MagazineDetailSerializer,
    MagazineFeaturedSerializer,
    MagazineHomeResponseSerializer,
    MagazineListSerializer,
    MagazineAllResponseSerializer,
    MagazineHomePageSerializer,
)
from apps.products.models import (
    Product,
    ProductImage,
    ProductVariant,
)
from apps.shared.cache.list_cache import (
    CachedRetrieveMixin,
    cached_action_response,
    DEFAULT_HOME_TTL,
)
from apps.shared.cache import namespaces as ns
from utils.paginators import StandardResultPagination


class MagazineViewSet(CachedRetrieveMixin, viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    pagination_class = StandardResultPagination
    cache_namespace = ns.MAGAZINE_DETAIL
    cache_ttl = 60 * 10
    cache_lookup_kwarg = "slug"

    def get_queryset(self):
        queryset = (
            Magazine.objects.filter(is_published=True)
            .select_related("category")
            .order_by("-published_at")
        )

        if self.action == "retrieve":
            queryset = queryset.prefetch_related(
                Prefetch(
                    "related_products",
                    queryset=(
                        Product.objects.select_related("brand")
                        .prefetch_related(
                            Prefetch(
                                "images",
                                queryset=ProductImage.objects.order_by(
                                    "-is_primary",
                                    "-created_at",
                                ),
                                to_attr="ordered_images",
                            ),
                            Prefetch(
                                "variants",
                                queryset=ProductVariant.objects.filter(
                                    is_active=True
                                ).order_by("price"),
                                to_attr="active_variants",
                            ),
                        )
                        .order_by("-created_at")
                    ),
                    to_attr="prefetched_related_products",
                ),
                Prefetch(
                    "related_articles",
                    queryset=(
                        Magazine.objects.filter(is_published=True)
                        .select_related("category")
                        .order_by("-published_at")
                    ),
                    to_attr="prefetched_related_articles",
                ),
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return MagazineDetailSerializer
        return MagazineListSerializer

    @extend_schema(responses=MagazineHomeResponseSerializer)
    @action(detail=False, methods=["get"], url_path="home")
    def home(self, request):
        def build():
            articles = self.get_queryset()[:5]
            return {
                "articles": MagazineHomePageSerializer(
                    articles,
                    many=True,
                    context={"request": request},
                ).data,
            }

        return cached_action_response(
            ns.MAGAZINE_HOME,
            request,
            build,
            ttl=DEFAULT_HOME_TTL,
        )

    @extend_schema(responses=MagazineArchiveResponseSerializer)
    def list(self, request, *args, **kwargs):
        def build():
            queryset = self.get_queryset()
            featured_article = queryset.filter(is_featured=True).first()
            if featured_article is None:
                featured_article = queryset.first()
            latest_articles = queryset[:3]
            categories = MagazineCategory.objects.all().order_by("name")
            return {
                "categories": MagazineCategorySerializer(categories, many=True).data,
                "featured_article": (
                    MagazineFeaturedSerializer(
                        featured_article,
                        context={"request": request},
                    ).data
                    if featured_article
                    else None
                ),
                "latest_articles": MagazineListSerializer(
                    latest_articles,
                    many=True,
                    context={"request": request},
                ).data,
            }

        return cached_action_response(
            ns.MAGAZINE_LIST,
            request,
            build,
            ttl=DEFAULT_HOME_TTL,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="شماره صفحه",
            ),
            OpenApiParameter(
                name="page_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="تعداد مقالات در هر صفحه",
            ),
            OpenApiParameter(
                name="category",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="فیلتر بر اساس slug دسته‌بندی",
            ),
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="جستجو در مقالات",
            ),
        ],
        responses=MagazineAllResponseSerializer,
    )
    @action(detail=False, methods=["get"], url_path="all")
    def all(self, request):
        def build():
            queryset = self.get_queryset()
            category = request.query_params.get("category")
            if category:
                queryset = queryset.filter(category__slug=category)
            search = request.query_params.get("search")
            if search:
                queryset = queryset.filter(
                    Q(title__icontains=search)
                    | Q(short_description__icontains=search)
                    | Q(content__icontains=search)
                ).distinct()

            categories = MagazineCategory.objects.all().order_by("name")
            page = self.paginate_queryset(queryset)
            if page is not None:
                serialized_articles = MagazineListSerializer(
                    page,
                    many=True,
                    context={"request": request},
                ).data
                paginated_data = self.get_paginated_response(serialized_articles).data
            else:
                paginated_data = {
                    "results": MagazineListSerializer(
                        queryset,
                        many=True,
                        context={"request": request},
                    ).data,
                }
            return {
                "categories": MagazineCategorySerializer(categories, many=True).data,
                "articles": paginated_data,
            }

        return cached_action_response(
            ns.MAGAZINE_ALL,
            request,
            build,
            ttl=60 * 5,
        )
