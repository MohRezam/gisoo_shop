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
        verbose_name=_("phone number"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("created at"),
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("updated at"),
    )

    class Meta:
        verbose_name = _("guest identity")
        verbose_name_plural = _("guest identities")

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
        verbose_name=_("guest"),
    )

    token = models.CharField(
        max_length=64,
        unique=True,
        editable=False,
        verbose_name=_("token"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("created at"),
    )

    last_used_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("last used at"),
    )

    expires_at = models.DateTimeField(
        verbose_name=_("expires at"),
    )

    class Meta:
        verbose_name = _("guest device access")
        verbose_name_plural = _("guest device accesses")

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
        verbose_name=_("consultation"),
    )

    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.PROTECT,
        related_name="consultation_recommendations",
        verbose_name=_("product variant"),
    )

    explanation = models.TextField(
        blank=True,
        default="",
        verbose_name=_("explanation"),
    )

    usage_instruction = models.TextField(
        blank=True,
        default="",
        verbose_name=_("usage instruction"),
    )

    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("display order"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("created at"),
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

    def __str__(self):
        return (
            f"{self.consultation.full_name} "
            f"→ {self.variant}"
        )


class ConsultationRecommendationPack(models.Model):
    consultation = models.ForeignKey(
        ConsultationRequest,
        on_delete=models.CASCADE,
        related_name="recommendation_packs",
        verbose_name=_("consultation"),
    )

    title = models.CharField(
        max_length=255,
        verbose_name=_("title"),
    )

    description = models.TextField(
        blank=True,
        default="",
        verbose_name=_("description"),
    )

    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("display order"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("created at"),
    )

    class Meta:
        ordering = [
            "display_order",
            "created_at",
        ]

        verbose_name = _("consultation recommendation pack")
        verbose_name_plural = _(
            "consultation recommendation packs"
        )

    def __str__(self):
        return (
            f"{self.consultation.full_name} "
            f"→ {self.title}"
        )


class ConsultationRecommendationPackItem(models.Model):
    pack = models.ForeignKey(
        ConsultationRecommendationPack,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("pack"),
    )

    recommendation = models.ForeignKey(
        ConsultationRecommendation,
        on_delete=models.CASCADE,
        related_name="pack_items",
        verbose_name=_("recommendation"),
    )

    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("display order"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("created at"),
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

        verbose_name = _(
            "consultation recommendation pack item"
        )
        verbose_name_plural = _(
            "consultation recommendation pack items"
        )

    def clean(self):
        if (
                self.pack_id
                and self.recommendation_id
                and self.pack.consultation_id
                != self.recommendation.consultation_id
        ):
            raise ValidationError(
                _(
                    "Pack and recommendation "
                    "must belong to the same consultation."
                )
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.pack.title} → "
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

    def __str__(self):
        return (
            f"{self.guest.phone_number} "
            f"- {self.created_at}"
        )
