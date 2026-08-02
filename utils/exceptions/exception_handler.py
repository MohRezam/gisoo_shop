import logging

from django.http.response import Http404
from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler

from utils.general.logger import Logger

logger = logging.getLogger("custom")


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    request = context.get("request")
    view = context.get("view")

    if response is not None:
        if isinstance(exc, ValidationError):
            exc.default_code = "invalid_input"
            exc.default_detail = _("Some field is required.")
        elif isinstance(exc, Http404):
            exc.default_code = "no_match_found"
            exc.default_detail = _("No match found.")

        response.data = _handle_generic_error(exc)

        Logger.error(
            logger=logger,
            title="API-Exception",
            message=f"{str(exc)}",
            additional_data={
                "method": request.method if request else None,
                "url": request.path if request else None,
                "params": (
                    request.data if request and hasattr(request, "data") else None
                ),
                "user": (
                    request.user.id
                    if request
                    and hasattr(request, "user")
                    and request.user.is_authenticated
                    else None
                ),
                "status_code": response.status_code,
                "error_info": str(getattr(exc, "detail", str(exc))),
                "view": view.__class__.__name__ if view else None,
                "user_agent": request.headers.get("User-Agent") if request else None,
                "host": request.get_host() if request else None,
                "origin": request.headers.get("Origin") if request else None,
                "referer": request.headers.get("Referer") if request else None,
                "source_ip": request.META.get("REMOTE_ADDR") if request else None,
            },
        )

    return response


def _handle_generic_error(exc):
    try:
        version = exc.version
    except Exception:
        version = "v1"

    code = getattr(exc, "default_code", None)
    try:
        get_codes = getattr(exc, "get_codes", None)
        code = get_codes()
    except Exception:
        pass

    return {
        "error": {
            "code": code,
            "detail": getattr(exc, "detail", None),
            "version": version,
        }
    }
