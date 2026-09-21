from rest_framework import serializers

from apps.home.models import Banner, Slider


class BannerSerializer(serializers.ModelSerializer):
    link = serializers.SerializerMethodField()

    class Meta:
        model = Banner
        fields = (
            "id",
            "image",
            "link",
        )

    def get_link(self, obj):
        if obj.link_type == obj.LinkType.PRODUCT:
            if obj.product_id is None or obj.product is None:
                return None
            return f"/products/{obj.product.slug}/"

        if obj.link_type == obj.LinkType.CATEGORY:
            if obj.category_id is None or obj.category is None:
                return None
            return f"/categories/{obj.category.slug}/"

        if obj.link_type == obj.LinkType.CUSTOM:
            return obj.custom_url

        return None


class SliderSerializer(serializers.ModelSerializer):
    link = serializers.SerializerMethodField()

    class Meta:
        model = Slider
        fields = (
            "id",
            "image",
            "link",
        )

    def get_link(self, obj):
        if obj.link_type == obj.LinkType.PRODUCT:
            if obj.product_id is None or obj.product is None:
                return None
            return f"/products/{obj.product.slug}/"

        if obj.link_type == obj.LinkType.CATEGORY:
            if obj.category_id is None or obj.category is None:
                return None
            return f"/categories/{obj.category.slug}/"

        if obj.link_type == obj.LinkType.CUSTOM:
            return obj.custom_url

        return None
