from rest_framework import serializers

from apps.products.models import Banner


class BannerSerializer(serializers.ModelSerializer):
    link = serializers.SerializerMethodField()

    class Meta:
        model = Banner
        fields = (
            "id",
            "title",
            "image",
            "link",
        )

    def get_link(self, obj):
        if obj.link_type == obj.LinkType.PRODUCT:
            return f"/products/{obj.product.slug}/"

        if obj.link_type == obj.LinkType.CATEGORY:
            return f"/categories/{obj.category.slug}/"

        if obj.link_type == obj.LinkType.CUSTOM:
            return obj.custom_url

        return None