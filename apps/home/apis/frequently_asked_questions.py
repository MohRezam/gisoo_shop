from django.db.models import Prefetch
from drf_spectacular.utils import  extend_schema
from rest_framework import generics

from apps.home.models import FAQCategory, FAQ
from apps.home.serializers.frequently_asked_questions import FAQCategorySerializer
from utils.paginators import StandardResultPagination


@extend_schema(
    tags=["Home"],
    summary="Get FAQ List",
    description="Returns active FAQ for the home page.",
)
class FAQListAPIView(generics.ListAPIView):
    serializer_class = FAQCategorySerializer
    pagination_class = StandardResultPagination

    def get_queryset(self):
        active_faqs = FAQ.objects.filter(
            is_active=True,
        ).order_by(
            "ordering",
            "id",
        )

        return (
            FAQCategory.objects
            .filter(is_active=True)
            .prefetch_related(
                Prefetch(
                    "faqs",
                    queryset=active_faqs,
                )
            )
            .order_by(
                "ordering",
                "id",
            )
        )
