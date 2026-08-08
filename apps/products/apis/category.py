from drf_spectacular.utils import (
    extend_schema,
)

from rest_framework.generics import (
    ListAPIView,

)

from apps.products.models import (
    Category,

)
from apps.products.serializers import (
    CategorySerializer,

)
from utils.paginators import StandardResultPagination


@extend_schema(
    tags=["Products"],
    summary="List Categories",
)
class CategoryListAPIView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = []
    pagination_class = StandardResultPagination

