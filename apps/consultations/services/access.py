from django.shortcuts import get_object_or_404
from rest_framework.exceptions import (
    NotAuthenticated,
    PermissionDenied,
)

from apps.consultations.models import ConsultationRequest
from apps.consultations.services import get_guest_by_token
from core_gisoo_backend.settings.components.constants import GUEST_CONSULTATION_COOKIE_NAME


def get_accessible_consultation(
    *,
    consultation_id,
    request,
):
    consultation = get_object_or_404(
        ConsultationRequest.objects.select_related(
            "user",
            "guest",
            "hair_problem",
        ),
        id=consultation_id,
    )

    # -----------------------------------------
    # AUTHENTICATED USER
    # -----------------------------------------

    if request.user.is_authenticated:
        if consultation.user_id != request.user.id:
            raise PermissionDenied(
                "شما به این درخواست مشاوره دسترسی ندارید."
            )

        return consultation

    # -----------------------------------------
    # GUEST
    # -----------------------------------------

    guest_token = request.COOKIES.get(
        GUEST_CONSULTATION_COOKIE_NAME,
    )

    if not guest_token:
        raise NotAuthenticated(
            "Guest access token الزامی است."
        )

    guest = get_guest_by_token(
        guest_token,
    )

    if guest is None:
        raise NotAuthenticated(
            "Guest access token معتبر نیست."
        )

    if consultation.guest_id != guest.id:
        raise PermissionDenied(
            "شما به این درخواست مشاوره دسترسی ندارید."
        )

    return consultation