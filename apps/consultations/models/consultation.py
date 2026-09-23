import secrets
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class GuestIdentity(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    phone_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="شماره تلفن",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ به‌روزرسانی",
    )

    class Meta:
        verbose_name = "هویت مهمان"
        verbose_name_plural = "هویت‌های مهمان"

    def __str__(self):
        return self.phone_number


class GuestDeviceAccess(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    guest = models.ForeignKey(
        GuestIdentity,
        on_delete=models.CASCADE,
        related_name="device_accesses",
        verbose_name="مهمان",
    )

    token = models.CharField(
        max_length=64,
        unique=True,
        editable=False,
        verbose_name="توکن",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    last_used_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین استفاده",
    )

    expires_at = models.DateTimeField(
        verbose_name="تاریخ انقضا",
    )

    class Meta:
        verbose_name = "دسترسی دستگاه مهمان"
        verbose_name_plural = "دسترسی‌های دستگاه مهمان"

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.guest.phone_number} - {self.id}"


class ConsultationRequest(models.Model):
    class Gender(models.TextChoices):
        FEMALE = "female", "زن"
        MALE = "male", "مرد"

    class Duration(models.TextChoices):
        LESS_THAN_MONTH = (
            "less_than_month",
            "کمتر از یک ماه",
        )

        ONE_TO_THREE_MONTHS = (
            "one_to_three_months",
            "یک تا سه ماه",
        )

        MORE_THAN_THREE_MONTHS = (
            "more_than_three_months",
            "بیشتر از سه ماه",
        )

    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار"
        COMPLETED = "completed", "تکمیل‌شده"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="consultation_requests",
        null=True,
        blank=True,
        verbose_name="کاربر",
    )

    guest = models.ForeignKey(
        GuestIdentity,
        on_delete=models.SET_NULL,
        related_name="consultation_requests",
        null=True,
        blank=True,
        verbose_name="مهمان",
    )

    full_name = models.CharField(
        max_length=150,
        verbose_name="نام کامل",
    )

    phone_number = models.CharField(
        max_length=20,
        verbose_name="شماره موبایل",
    )

    gender = models.CharField(
        max_length=20,
        choices=Gender.choices,
        verbose_name="جنسیت",
    )

    hair_problem = models.ForeignKey(
        "products.HairProblem",
        on_delete=models.PROTECT,
        related_name="consultation_requests",
        verbose_name="مشکل مو",
    )

    duration = models.CharField(
        max_length=50,
        choices=Duration.choices,
        verbose_name="مدت مشکل",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="وضعیت",
    )

    request_phone_consultation = models.BooleanField(
        default=False,
        verbose_name="درخواست مشاوره تلفنی",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین به‌روزرسانی",
    )

    class Meta:
        verbose_name = "درخواست مشاوره"
        verbose_name_plural = "درخواست‌های مشاوره"

        ordering = [
            "-created_at",
        ]

        constraints = [
            models.CheckConstraint(
                condition=(
                        (
                                models.Q(user__isnull=False)
                                & models.Q(guest__isnull=True)
                        )
                        |
                        (
                                models.Q(user__isnull=True)
                                & models.Q(guest__isnull=False)
                        )
                ),
                name="consultation_has_exactly_one_owner",
            ),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.phone_number}"


class ConsultationRecommendation(models.Model):
    consultation = models.ForeignKey(
        ConsultationRequest,
        on_delete=models.CASCADE,
        related_name="recommendations",
        verbose_name="مشاوره",
    )

    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.PROTECT,
        related_name="consultation_recommendations",
        verbose_name="واریانت محصول",
    )

    explanation = models.TextField(
        blank=True,
        default="",
        verbose_name="توضیح",
    )

    usage_instruction = models.TextField(
        blank=True,
        default="",
        verbose_name="دستور مصرف",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    class Meta:
        ordering = [
            "display_order",
            "created_at",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "consultation",
                    "variant",
                ],
                name="unique_consultation_variant_recommendation",
            ),
        ]

        verbose_name = "پیشنهاد محصول مشاوره"
        verbose_name_plural = "پیشنهادهای محصول مشاوره"

    def __str__(self):
        variant = self.variant
        product = getattr(variant, "product", None)
        title = getattr(product, "title", None) or str(variant)
        sku = getattr(variant, "sku", "") or ""
        if sku:
            return f"{title} ({sku})"
        return title


class ConsultationRecommendationPack(models.Model):
    consultation = models.ForeignKey(
        ConsultationRequest,
        on_delete=models.CASCADE,
        related_name="recommendation_packs",
        verbose_name="مشاوره",
    )

    title = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="عنوان گروه",
        help_text="اختیاری — مثلاً «روتین روزانه»",
    )

    description = models.TextField(
        blank=True,
        default="",
        verbose_name="متن کلی گروه",
        help_text=(
            "متن مشترک برای کل گروه محصولات — "
            "مثلاً «این محصولات را به‌صورت روتین استفاده کنید»"
        ),
    )

    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    class Meta:
        ordering = [
            "display_order",
            "created_at",
        ]

        verbose_name = "گروه پیشنهاد محصول"
        verbose_name_plural = "گروه‌های پیشنهاد محصول"

    def __str__(self):
        label = self.title.strip() or (self.description[:40] if self.description else "گروه")
        return (
            f"{self.consultation.full_name} "
            f"→ {label}"
        )


class ConsultationRecommendationPackItem(models.Model):
    pack = models.ForeignKey(
        ConsultationRecommendationPack,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="گروه",
    )

    recommendation = models.ForeignKey(
        ConsultationRecommendation,
        on_delete=models.CASCADE,
        related_name="pack_items",
        verbose_name="پیشنهاد محصول",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    class Meta:
        ordering = [
            "display_order",
            "created_at",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "pack",
                    "recommendation",
                ],
                name="unique_pack_recommendation",
            ),
        ]

        verbose_name = "محصول داخل گروه"
        verbose_name_plural = "محصولات داخل گروه"

    def clean(self):
        if (
                self.pack_id
                and self.recommendation_id
                and self.pack.consultation_id
                != self.recommendation.consultation_id
        ):
            raise ValidationError(
                _(
                    "گروه و پیشنهاد محصول باید متعلق به یک مشاوره باشند."
                )
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        pack_label = self.pack.title.strip() or "گروه"
        return (
            f"{pack_label} → "
            f"{self.recommendation}"
        )


class GuestOTP(models.Model):
    guest = models.ForeignKey(
        GuestIdentity,
        on_delete=models.CASCADE,
        related_name="otps",
    )

    code = models.CharField(
        max_length=6,
    )

    expires_at = models.DateTimeField()

    attempts = models.PositiveIntegerField(
        default=0,
    )

    is_used = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]
        verbose_name = "کد تأیید مهمان"
        verbose_name_plural = "کدهای تأیید مهمان"

    def __str__(self):
        return (
            f"{self.guest.phone_number} "
            f"- {self.created_at}"
        )
