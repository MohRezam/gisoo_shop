from django.db import models
from django.utils.translation import gettext_lazy as _

from django.core.exceptions import ValidationError
from django.db.models import Q

from apps.shared.models.base import BaseModel
from core_gisoo_backend.storage_backends.locations import product_image_path
from django.db.models import F
from django.utils import timezone


class Product(BaseModel):
    category = models.ForeignKey(
        "products.Category",
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="دسته‌بندی",
    )

    brand = models.ForeignKey(
        "products.Brand",
        on_delete=models.SET_NULL,
        related_name="products",
        blank=True,
        null=True,
        verbose_name="برند",
    )

    related_products = models.ManyToManyField(
        "self",
        through="ProductRelatedProduct",
        symmetrical=False,
        related_name="related_from_products",
        blank=True,
        verbose_name="محصولات مرتبط",
    )

    title = models.CharField(
        max_length=255,
        verbose_name="عنوان",
    )

    slug = models.SlugField(
        unique=True,
        verbose_name="اسلاگ",
    )

    short_description = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="توضیحات کوتاه",
    )

    description = models.TextField(
        verbose_name="توضیحات",
    )

    is_available = models.BooleanField(
        default=True,
        verbose_name="موجود",
    )

    show_in_special_offer = models.BooleanField(
        default=False,
        verbose_name="نمایش در پیشنهاد ویژه",
        help_text=(
            "فقط محصولاتی که حداقل یک واریانت با قیمت تخفیف‌خورده دارند "
            "می‌توانند در پیشنهاد ویژه نمایش داده شوند."
        ),
    )

    hair_problems = models.ManyToManyField(
        "products.HairProblem",
        blank=True,
        related_name="products",
        verbose_name="مشکل مو",
    )

    hair_types = models.ManyToManyField(
        "products.HairType",
        blank=True,
        related_name="products",
        verbose_name="نوع مو",
    )

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def has_active_discount(self) -> bool:
        if not self.pk:
            return False

        return self.variants.filter(
            is_active=True,
            discounted_price__isnull=False,
            discounted_price__lt=F("price"),
        ).exists()

    def clean(self):
        super().clean()

        if self.show_in_special_offer and self.pk:
            if not self.has_active_discount():
                raise ValidationError({
                    "show_in_special_offer": (
                        "برای افزودن به پیشنهاد ویژه، محصول باید "
                        "حداقل یک واریانت فعال با قیمت تخفیف‌خورده داشته باشد."
                    ),
                })


class ProductRelatedProduct(BaseModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="related_product_relations",
        verbose_name=_("product"),
    )

    related_product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="related_to_relations",
        verbose_name=_("related product"),
    )

    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("display order"),
    )

    class Meta:
        verbose_name = "محصول مرتبط"
        verbose_name_plural = "محصولات مرتبط"

        ordering = [
            "display_order",
            "-created_at",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "product",
                    "related_product",
                ],
                name="unique_product_related_product",
            ),
            models.CheckConstraint(
                condition=~models.Q(
                    product=models.F("related_product")
                ),
                name="product_cannot_be_related_to_itself",
            ),
        ]

    def __str__(self):
        return (
            f"{self.product.title} → "
            f"{self.related_product.title}"
        )


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
        verbose_name = "تصویر محصول"
        verbose_name_plural = "تصاویر محصول"
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
        verbose_name="محصول",
    )

    sku = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="کد کالا",
    )

    price = models.PositiveBigIntegerField(
        verbose_name="قیمت",
        default=0
    )

    discounted_price = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="قیمت تخفیف‌خورده",
    )

    stock = models.PositiveIntegerField(
        default=0,
        verbose_name="موجودی",
    )

    volume = models.PositiveIntegerField(
        verbose_name="حجم (میلی‌لیتر)",
        default=0,
        help_text=_("Volume in milliliter."),
    )

    expiration_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="تاریخ انقضا",
    )
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    class Meta:
        verbose_name = "تنوع محصول"
        verbose_name_plural = "تنوع‌های محصول"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=(
                        Q(discounted_price__isnull=True)
                        | Q(discounted_price__lt=F("price"))
                ),
                name="discounted_price_less_than_price",
            ),
            models.UniqueConstraint(
                fields=["product", "volume"],
                name="unique_volume_per_product",
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
        verbose_name = "ویژگی"
        verbose_name_plural = "ویژگی‌ها"
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
        verbose_name = "مقدار ویژگی"
        verbose_name_plural = "مقادیر ویژگی"
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
        verbose_name = "ویژگی تنوع"
        verbose_name_plural = "ویژگی‌های تنوع"
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
        verbose_name = "ویژگی محصول"
        verbose_name_plural = "ویژگی‌های محصول"
        ordering = ["display_order", "-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["product", "attribute"],
                name="unique_product_attribute",
            )
        ]

    def __str__(self):
        return f"{self.product.title} - {self.attribute.name}"



class DiscountCampaign(BaseModel):
    title = models.CharField(
        max_length=255,
        verbose_name=_("title"),
    )

    starts_at = models.DateTimeField(
        verbose_name=_("starts_at"),
    )

    ends_at = models.DateTimeField(
        verbose_name=_("ends_at"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("is_active"),
    )

    singleton_key = models.BooleanField(
        default=True,
        unique=True,
        editable=False,
    )

    class Meta:
        verbose_name = "کمپین تخفیف"
        verbose_name_plural = "کمپین تخفیف"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()

        if self.starts_at and self.ends_at:
            if self.ends_at <= self.starts_at:
                raise ValidationError({
                    "ends_at": _(
                        "End time must be after start time."
                    )
                })

    @property
    def is_running(self):
        if not self.starts_at or not self.ends_at:
            return False

        now = timezone.now()

        return (
            self.is_active
            and self.starts_at <= now < self.ends_at
        )

    @property
    def is_expired(self):
        if not self.ends_at:
            return False

        return timezone.now() >= self.ends_at

    @property
    def is_upcoming(self):
        if not self.starts_at:
            return False

        now = timezone.now()

        return (
            self.is_active
            and now < self.starts_at
        )