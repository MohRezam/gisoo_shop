from django_filters import rest_framework as filters

from apps.products.models import Product


class ProductFilter(filters.FilterSet):
    category = filters.NumberFilter(
        field_name="category_id",
    )

    brand = filters.NumberFilter(
        field_name="brand_id",
    )

    min_price = filters.NumberFilter(
        field_name="variants__price",
        lookup_expr="gte",
    )

    max_price = filters.NumberFilter(
        field_name="variants__price",
        lookup_expr="lte",
    )

    hair_problem = filters.NumberFilter(
        field_name="hair_problems__id",
    )

    hair_type = filters.NumberFilter(
        field_name="hair_types__id",
    )

    class Meta:
        model = Product

        fields = [
            "category",
            "brand",
            "min_price",
            "max_price",
            "hair_problem",
            "hair_type"
        ]