from json import JSONDecodeError
import logging

import requests
from decouple import config

from apps.notifications.services.sms.base import (
    SMSProvider,
    SMSResult,
)


logger = logging.getLogger("sms")


class MelipayamakProvider(SMSProvider):

    def __init__(self):
        self.api_url = config(
            "MELIPAYAMAK_API"
        )

    def send_pattern(
        self,
        *,
        recipient: str,
        pattern_id: int,
        args: list[str],
    ) -> SMSResult:

        data = {
            "bodyId": pattern_id,
            "to": recipient,
            "args": [
                str(arg)
                for arg in args
            ],
        }

        try:
            response = requests.post(
                self.api_url,
                json=data,
                timeout=10,
            )

            response.raise_for_status()

        except requests.exceptions.RequestException as exc:
            logger.exception(
                "Melipayamak request failed "
                "for %s: %s",
                recipient,
                exc,
            )

            return SMSResult(
                success=False,
                error=str(exc),
            )

        try:
            json_response = response.json()

        except JSONDecodeError:
            logger.error(
                "Melipayamak returned "
                "non-JSON response: %s",
                response.text,
            )

            return SMSResult(
                success=False,
                error=(
                    "Non-JSON response "
                    "from SMS provider."
                ),
                response=response,
            )

        rec_id = json_response.get(
            "recId"
        )

        if not rec_id:
            logger.error(
                "Melipayamak SMS failed "
                "for %s: %s",
                recipient,
                json_response,
            )

            return SMSResult(
                success=False,
                error=str(json_response),
                response=json_response,
            )

        logger.info(
            "SMS sent to %s. recId=%s",
            recipient,
            rec_id,
        )

        return SMSResult(
            success=True,
            provider_message_id=str(rec_id),
            response=json_response,
        )

    def send_text(
        self,
        *,
        recipient: str,
        message: str,
    ) -> SMSResult:

        # Intentionally not implemented yet.
        #
        # Transactional SMS messages should use
        # registered patterns.
        #
        # Marketing SMS will have a separate flow.

        return SMSResult(
            success=False,
            error=(
                "Direct text SMS is not implemented."
            ),
        )