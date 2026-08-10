from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import generics

from apps.home.models import FAQCategory, FAQ
from apps.home.serializers.frequently_asked_questions import FAQCategorySerializer, FAQSerializer
from utils.paginators import StandardResultPagination


@extend_schema(
    tags=["Home"],
    summary="Get FAQ Category List",
    description="Returns active FAQ Category for the home page.",
)
class FAQCategoryListAPIView(generics.ListAPIView):
    serializer_class = FAQCategorySerializer
    pagination_class = StandardResultPagination

    def get_queryset(self):
        return FAQCategory.objects.filter(
            is_active=True
        )


@extend_schema(
    tags=["Home"],
    parameters=[
        OpenApiParameter(
            name="category_slug",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
            description="شناسه دسته‌بندی سوالات متداول",
        ),
    ],
)
class FAQListAPIView(generics.ListAPIView):
    serializer_class = FAQSerializer
    pagination_class = StandardResultPagination

    def get_queryset(self):
        queryset = FAQ.objects.filter(
            is_active=True,
            category__is_active=True,
        ).select_related("category")

        category_slug = self.request.query_params.get("category_slug")
        if category_slug:
            queryset = queryset.filter(
                category__slug=category_slug
            )

        return queryset
