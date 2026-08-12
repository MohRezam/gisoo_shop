from django.db.models import Prefetch, Q

from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.magazine.models import (
    Magazine,
    MagazineCategory,
)
from apps.magazine.serializers import (
    MagazineArchiveResponseSerializer,
    MagazineCategorySerializer,
    MagazineDetailSerializer,
    MagazineFeaturedSerializer,
    MagazineHomeResponseSerializer,
    MagazineListSerializer, MagazineAllResponseSerializer,
)
from apps.products.models import (
    Product,
    ProductImage,
    ProductVariant,
)
from utils.paginators import StandardResultPagination


class MagazineViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    pagination_class = StandardResultPagination

    def get_queryset(self):
        queryset = (
            Magazine.objects
            .filter(is_published=True)
            .select_related("category")
            .order_by("-published_at")
        )

        if self.action == "retrieve":
            queryset = queryset.prefetch_related(

                Prefetch(
                    "related_products",
                    queryset=(
                        Product.objects
                        .select_related("brand")
                        .prefetch_related(
                            Prefetch(
                                "images",
                                queryset=(
                                    ProductImage.objects
                                    .order_by(
                                        "-is_primary",
                                        "-created_at",
                                    )
                                ),
                                to_attr="ordered_images",
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
                        .order_by("-created_at")[:8]
                    ),
                    to_attr="prefetched_related_products",
                ),


                Prefetch(
                    "related_articles",
                    queryset=(
                        Magazine.objects
                        .filter(is_published=True)
                        .select_related("category")
                        .order_by("-published_at")[:6]
                    ),
                    to_attr="prefetched_related_articles",
                ),
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return MagazineDetailSerializer

        return MagazineListSerializer

    @extend_schema(
        responses=MagazineHomeResponseSerializer,
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="home",
    )
    def home(self, request):
        queryset = self.get_queryset()

        articles = queryset[:5]

        return Response({
            "articles": MagazineListSerializer(
                articles,
                many=True,
                context={
                    "request": request,
                },
            ).data,
        })

    @extend_schema(
        responses=MagazineArchiveResponseSerializer,
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        featured_article = (
            queryset
            .filter(is_featured=True)
            .first()
        )

        if featured_article is None:
            featured_article = queryset.first()

        latest_articles = queryset[:3]

        categories = (
            MagazineCategory.objects
            .all()
            .order_by("name")
        )

        return Response({
            "categories": MagazineCategorySerializer(
                categories,
                many=True,
            ).data,

            "featured_article": (
                MagazineFeaturedSerializer(
                    featured_article,
                    context={
                        "request": request,
                    },
                ).data
                if featured_article
                else None
            ),

            "latest_articles": MagazineListSerializer(
                latest_articles,
                many=True,
                context={
                    "request": request,
                },
            ).data,
        })

    @extend_schema(
        responses=MagazineAllResponseSerializer,
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="all",
    )
    def all(self, request):
        queryset = self.get_queryset()

        category = request.query_params.get("category")

        if category:
            queryset = queryset.filter(
                category__slug=category
            )

        search = request.query_params.get("search")

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(short_description__icontains=search)
                | Q(content__icontains=search)
            ).distinct()

        categories = (
            MagazineCategory.objects
            .all()
            .order_by("name")
        )

        page = self.paginate_queryset(queryset)

        if page is not None:
            serialized_articles = MagazineListSerializer(
                page,
                many=True,
                context={
                    "request": request,
                },
            ).data

            paginated_data = self.get_paginated_response(
                serialized_articles
            ).data
        else:
            paginated_data = {
                "results": MagazineListSerializer(
                    queryset,
                    many=True,
                    context={
                        "request": request,
                    },
                ).data,
            }

        return Response({
            "categories": MagazineCategorySerializer(
                categories,
                many=True,
            ).data,

            "articles": paginated_data,
        })