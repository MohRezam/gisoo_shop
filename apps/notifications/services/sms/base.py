from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class SMSResult:
    success: bool
    provider_message_id: str | None = None
    response: Any = None
    error: str | None = None


class SMSProvider(ABC):

    @abstractmethod
    def send_pattern(
        self,
        *,
        recipient: str,
        pattern_id: int,
        args: list[str],
    ) -> SMSResult:
        raise NotImplementedError

    @abstractmethod
    def send_text(
        self,
        *,
        recipient: str,
        message: str,
    ) -> SMSResult:
        raise NotImplementedError