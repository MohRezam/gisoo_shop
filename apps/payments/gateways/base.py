from abc import ABC, abstractmethod


class BasePaymentGateway(ABC):

    @abstractmethod
    def create_payment(
        self,
        *,
        payment,
        callback_url: str,
    ):
        """
        Create payment request
        and return redirect URL.
        """
        raise NotImplementedError


    @abstractmethod
    def verify_payment(
        self,
        *,
        payment,
        authority: str,
    ):
        """
        Verify payment after callback.
        """
        raise NotImplementedError