from drf_spectacular.utils import extend_schema
from rest_framework import generics

from apps.home.models import CustomerSatisfaction
from apps.home.serializers import CustomerSatisfactionSerializer


@extend_schema(
    tags=["Home"],
    summary="Get Customers Satisfactions",
    description="Returns Active Customers Satisfactions.",
)
class CustomerSatisfactionListAPIView(generics.ListAPIView):
    serializer_class = CustomerSatisfactionSerializer

    def get_queryset(self):
        return CustomerSatisfaction.objects.filter(
            is_active=True
        )
