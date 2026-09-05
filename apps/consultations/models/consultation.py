import secrets
import uuid

from django.conf import settings
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
        FEMALE = "female", _("Female")
        MALE = "male", _("Male")

    class Duration(models.TextChoices):
        LESS_THAN_MONTH = (
            "less_than_month",
            _("Less than a month"),
        )

        ONE_TO_THREE_MONTHS = (
            "one_to_three_months",
            _("One to three months"),
        )

        MORE_THAN_THREE_MONTHS = (
            "more_than_three_months",
            _("More than three months"),
        )

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        COMPLETED = "completed", _("Completed")

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
        verbose_name=_("user"),
    )

    guest = models.ForeignKey(
        GuestIdentity,
        on_delete=models.SET_NULL,
        related_name="consultation_requests",
        null=True,
        blank=True,
        verbose_name=_("guest"),
    )

    full_name = models.CharField(
        max_length=150,
        verbose_name=_("full name"),
    )

    phone_number = models.CharField(
        max_length=20,
        verbose_name=_("phone number"),
    )

    gender = models.CharField(
        max_length=20,
        choices=Gender.choices,
        verbose_name=_("gender"),
    )

    hair_problem = models.ForeignKey(
        "products.HairProblem",
        on_delete=models.PROTECT,
        related_name="consultation_requests",
        verbose_name=_("hair problem"),
    )

    duration = models.CharField(
        max_length=50,
        choices=Duration.choices,
        verbose_name=_("duration"),
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_("status"),
    )

    request_phone_consultation = models.BooleanField(
        default=False,
        verbose_name=_("phone consultation"),
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
        verbose_name = _("consultation request")
        verbose_name_plural = _("consultation requests")

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

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="consultation_recommendations",
        verbose_name=_("product"),
    )

    explanation = models.TextField(
        blank=True,
        default="",
        verbose_name=_("explanation"),
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
                    "product",
                ],
                name="unique_consultation_recommendation",
            ),
        ]

    def __str__(self):
        return (
            f"{self.consultation.full_name} "
            f"→ {self.product.title}"
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