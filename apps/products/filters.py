from django.db.models import Min, Q
from django.db.models.functions import Coalesce
from django_filters import rest_framework as filters

from apps.products.models import Product


def _ensure_effective_price(queryset):
    """
    Lowest active-variant selling price (sale if set, else list).
    Product list view already annotates this as `discounted_price`.
    """
    if "discounted_price" in queryset.query.annotations:
        return queryset
    return queryset.annotate(
        discounted_price=Min(
            Coalesce("variants__discounted_price", "variants__price"),
            filter=Q(variants__is_active=True),
        )
    )


class ProductFilter(filters.FilterSet):
    category = filters.NumberFilter(
        field_name="categories__id",
    )

    brand = filters.NumberFilter(
        field_name="brand_id",
    )

    min_price = filters.NumberFilter(method="filter_min_price")
    max_price = filters.NumberFilter(method="filter_max_price")

    hair_problem = filters.BaseInFilter(
        field_name="hair_problems__id",
        lookup_expr="in",
    )

    hair_type = filters.BaseInFilter(
        field_name="hair_types__id",
        lookup_expr="in",
    )

    class Meta:
        model = Product
        fields = [
            "category",
            "brand",
            "min_price",
            "max_price",
            "hair_problem",
            "hair_type",
        ]

    def filter_min_price(self, queryset, name, value):
        if value is None:
            return queryset
        # Filter on product effective price — not "any variant in range"
        # (which would show a cheaper default variant outside the chip range).
        return _ensure_effective_price(queryset).filter(
            discounted_price__gte=value,
        )

    def filter_max_price(self, queryset, name, value):
        if value is None:
            return queryset
        return _ensure_effective_price(queryset).filter(
            discounted_price__lte=value,
        )
