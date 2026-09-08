from django.core.exceptions import ValidationError
from django.db import transaction

from django.shortcuts import get_object_or_404

from apps.consultations.models import (
    GuestDeviceAccess,
)
from apps.cart.services import add_to_cart
from apps.consultations.models import (
    ConsultationRecommendation,
    ConsultationRequest,
)


def add_consultation_recommendations_to_cart(
        *,
        consultation,
        user,
        cart_uuid=None,
        recommendation_ids=None,
):
    if consultation.status != ConsultationRequest.Status.COMPLETED:
        raise ValidationError(
            "Consultation is not completed yet."
        )

    recommendations = (
        ConsultationRecommendation.objects
        .select_related(
            "variant",
            "variant__product",
        )
        .filter(
            consultation=consultation,
        )
    )

    if recommendation_ids is not None:
        requested_ids = set(recommendation_ids)

        recommendations = recommendations.filter(
            id__in=requested_ids,
        )

        found_ids = set(
            recommendations.values_list("id", flat=True)
        )

        invalid_ids = requested_ids - found_ids

        if invalid_ids:
            raise ValidationError(
                "One or more recommendations do not belong to this consultation."
            )

    recommendations = list(recommendations)

    if not recommendations:
        raise ValidationError(
            "No recommendations found."
        )

    current_cart_uuid = cart_uuid

    with transaction.atomic():
        for recommendation in recommendations:
            variant = recommendation.variant

            if not variant.is_active:
                raise ValidationError(
                    f"Product variant {variant.id} is not active."
                )

            if variant.stock < 1:
                raise ValidationError(
                    f"Product variant {variant.id} is out of stock."
                )

            cart = add_to_cart(
                cart_uuid=current_cart_uuid,
                user=user,
                variant_id=variant.id,
                quantity=1,
            )

            current_cart_uuid = str(cart.uuid)

    return cart


def get_accessible_consultation(
        *,
        consultation_id,
        user,
        guest_token=None,
):
    consultation = get_object_or_404(
        ConsultationRequest.objects.select_related(
            "user",
            "guest",
        ),
        id=consultation_id,
    )

    if user and user.is_authenticated:
        if consultation.user_id != user.id:
            raise ValidationError(
                "You do not have access to this consultation."
            )

        return consultation

    if not guest_token:
        raise ValidationError(
            "Guest token is required."
        )

    guest_access = (
        GuestDeviceAccess.objects
        .select_related("guest")
        .filter(
            token=guest_token,
            is_active=True,
        )
        .first()
    )

    if not guest_access:
        raise ValidationError(
            "Invalid guest token."
        )

    if guest_access.guest_id != consultation.guest_id:
        raise ValidationError(
            "You do not have access to this consultation."
        )

    return consultation
