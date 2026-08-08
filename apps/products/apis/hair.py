from drf_spectacular.utils import (
    extend_schema,
)
from rest_framework.generics import ListAPIView

from apps.products.models import HairProblem
from apps.products.serializers import HairProblemSerializer


@extend_schema(
    tags=["Hair Problems"],
    summary="List Hair Problems",
)
class HairProblemAPIView(ListAPIView):
    serializer_class = HairProblemSerializer
    queryset = HairProblem.objects.filter(is_active=True)
    filter_backends = []
    pagination_class = None
