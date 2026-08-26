import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


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
        REVIEWING = "reviewing", _("Reviewing")
        COMPLETED = "completed", _("Completed")

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
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
        ordering = ["-created_at"]

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
        verbose_name = _("consultation recommendation")
        verbose_name_plural = _("consultation recommendations")
        ordering = ["display_order", "id"]

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
            f"{self.consultation.full_name} - "
            f"{self.product.title}"
        )