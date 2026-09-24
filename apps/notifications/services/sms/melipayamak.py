import logging

from apps.notifications.services.sms.base import (
    SMSProvider,
    SMSResult,
)
from apps.sms.client import send_by_base_number


logger = logging.getLogger("sms")


class MelipayamakProvider(SMSProvider):
    """
    Compatibility wrapper around apps.sms SendByBaseNumber client.
    Prefer apps.sms.service.send_pattern_sms for new call sites.
    """

    def send_pattern(
        self,
        *,
        recipient: str,
        pattern_id: int,
        args: list[str],
    ) -> SMSResult:
        result = send_by_base_number(
            phone=recipient,
            body_id=int(pattern_id or 0),
            text_vars=[str(arg) for arg in args],
        )

        if result.get("success"):
            return SMSResult(
                success=True,
                provider_message_id=result.get("message_id"),
                response=result.get("provider_response"),
            )

        return SMSResult(
            success=False,
            error=result.get("error_message") or "SMS send failed.",
            response=result.get("provider_response"),
        )

    def send_text(
        self,
        *,
        recipient: str,
        message: str,
    ) -> SMSResult:
        return SMSResult(
            success=False,
            error=(
                "Direct text SMS is not implemented. "
                "Use registered patterns via send_pattern_sms."
            ),
        )
