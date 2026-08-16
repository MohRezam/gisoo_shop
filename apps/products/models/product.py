from django.db import models
from django.utils.translation import gettext_lazy as _

from django.core.exceptions import ValidationError
from django.db.models import Q

from apps.shared.models.base import BaseModel
from core_gisoo_backend.storage_backends.locations import product_image_path
from django.db.models import F


class Product(BaseModel):
    category = models.ForeignKey(
        "products.Category",
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name=_("category"),
    )

    brand = models.ForeignKey(
        "products.Brand",
        on_delete=models.SET_NULL,
        related_name="products",
        blank=True,
        null=True,
        verbose_name=_("brand"),
    )

    title = models.CharField(
        max_length=255,
        verbose_name=_("title"),
    )

    slug = models.SlugField(
        unique=True,
        verbose_name=_("slug"),
    )

    short_description = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("short_description"),
    )

    description = models.TextField(
        verbose_name=_("description"),
    )

    is_available = models.BooleanField(
        default=True,
        verbose_name=_("is_available"),
    )
    hair_problems = models.ManyToManyField(
        "products.HairProblem",
        blank=True,
        related_name="products",
        verbose_name=_("hair_problem"),
    )

    hair_types = models.ManyToManyField(
        "products.HairType",
        blank=True,
        related_name="products",
        verbose_name=_("hair_types"),
    )

    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("products")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class ProductImage(BaseModel):
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("product"),
    )

    image = models.ImageField(
        upload_to=product_image_path(),
        verbose_name=_("image"),
        null=True,
        blank=True
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name=_("Primary image"),
    )
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("alt_text"),
    )

    class Meta:
        verbose_name = _("product_image")
        verbose_name_plural = _("products_images")
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["product"],
                condition=Q(is_primary=True),
                name="unique_primary_product_image",
            )
        ]

    def __str__(self):
        return self.product.title

    def clean(self):
        super().clean()

        if not self.is_primary:
            return

        if not self.product_id:
            return

        exists = (
            ProductImage.objects
            .filter(
                product_id=self.product_id,
                is_primary=True,
            )
            .exclude(
                pk=self.pk,
            )
            .exists()
        )

        if exists:
            raise ValidationError(
                _("This product already has a primary image.")
            )


class ProductVariant(BaseModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants",
    )

    sku = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("sku"),
    )

    price = models.PositiveBigIntegerField(
        verbose_name=_("price"),
        default=0
    )

    discounted_price = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name=_("discounted_price"),
    )

    stock = models.PositiveIntegerField(
        default=0,
        verbose_name=_("stock"),
    )

    weight = models.PositiveIntegerField(
        verbose_name=_("Weight (g)"),
        default=0,
        help_text=_("Weight in grams."),
    )

    expiration_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("expiration_date"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("is_active"),
    )

    class Meta:
        verbose_name = _("product_variant")
        verbose_name_plural = _("product_variants")
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=(
                        Q(discounted_price__isnull=True)
                        | Q(discounted_price__lt=F("price"))
                ),
                name="discounted_price_less_than_price",
            ),
        ]

    def __str__(self):
        return f"{self.product.title} - {self.sku}"


class Attribute(BaseModel):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("attribute_name"),
    )

    slug = models.SlugField(
        unique=True,
        verbose_name=_("slug"),
    )

    is_variant = models.BooleanField(
        default=True,
        verbose_name=_("is_variant"),
    )

    class Meta:
        verbose_name = _("attribute")
        verbose_name_plural = _("attributes")
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class AttributeValue(BaseModel):
    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        related_name="values",
        verbose_name=_("attribute")
    )

    value = models.CharField(
        max_length=255,
        verbose_name=_("attribute_value"),
    )

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

    class Meta:
        verbose_name = _("attribute_value")
        verbose_name_plural = _("attributes_values")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["attribute", "value"],
                name="unique_attribute_value",
            )
        ]


class VariantAttribute(BaseModel):
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="attributes",
        verbose_name=_("variant")
    )

    value = models.ForeignKey(
        AttributeValue,
        on_delete=models.CASCADE,
        verbose_name=_("value")
    )

    def clean(self):
        super().clean()

        if not self.variant_id or not self.value_id:
            return

        attribute = self.value.attribute

        exists = (
            VariantAttribute.objects
            .filter(
                variant_id=self.variant_id,
                value__attribute=attribute,
            )
            .exclude(pk=self.pk)
            .exists()
        )

        if exists:
            raise ValidationError(
                _("This variant already has a value for this attribute.")
            )

    class Meta:
        verbose_name = _("variant_attribute")
        verbose_name_plural = _("variant_attributes")
        ordering = ["-created_at"]


class ProductAttribute(BaseModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="product_attributes",
        verbose_name=_("product"),
    )

    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        related_name="product_attributes",
        verbose_name=_("attribute"),
    )

    value = models.CharField(
        max_length=500,
        verbose_name=_("value"),
    )

    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("display_order"),
    )

    class Meta:
        verbose_name = _("product attribute")
        verbose_name_plural = _("product attributes")
        ordering = ["display_order", "-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["product", "attribute"],
                name="unique_product_attribute",
            )
        ]

    def __str__(self):
        return f"{self.product.title} - {self.attribute.name}"