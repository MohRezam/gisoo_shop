from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError

from apps.products.models import Product
from apps.reviews.models import ProductReview, ReviewStatus
from apps.reviews.serializers import ProductReviewSerializer, HomepageReviewSerializer


class ProductReviewListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ProductReviewSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    def get_product(self):
        return get_object_or_404(
            Product,
            pk=self.kwargs["product_id"],
        )

    def get_queryset(self):
        return (
            ProductReview.objects.filter(
                product_id=self.kwargs["product_id"],
                status=ReviewStatus.APPROVED,
            )
            .select_related("user", "product")
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        product = self.get_product()

        if ProductReview.objects.filter(
                user=self.request.user,
                product=product,
        ).exists():
            raise ValidationError(
                {
                    "detail": (
                        "You have already reviewed this product."
                    )
                }
            )

        serializer.save(
            user=self.request.user,
            product=product,
            status=ReviewStatus.PENDING,
        )


class HomepageReviewListAPIView(generics.ListAPIView):
    serializer_class = HomepageReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        featured_reviews = (
            ProductReview.objects
            .filter(
                status=ReviewStatus.APPROVED,
                is_featured=True,
            )
            .select_related(
                "product",
                "user",
            )
            .order_by(
                "homepage_order",
                "-created_at",
            )
        )

        if featured_reviews.exists():
            return featured_reviews

        approved_reviews = (
            ProductReview.objects
            .filter(
                status=ReviewStatus.APPROVED,
            )
            .select_related(
                "product",
                "user",
            )
            .order_by(
                "-created_at",
            )
        )

        reviews = []
        seen_products = set()

        for review in approved_reviews:
            if review.product_id in seen_products:
                continue

            reviews.append(review)
            seen_products.add(review.product_id)

            if len(reviews) == 10:
                break

        return reviews