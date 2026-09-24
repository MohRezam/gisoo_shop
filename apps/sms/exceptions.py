class SmsError(Exception):
    """Base SMS module error."""


class SmsConfigError(SmsError):
    """Missing credentials or bodyId."""


class SmsPatternError(SmsError):
    """Unknown pattern or invalid variables."""


class SmsProviderError(SmsError):
    """Provider returned a failure code or transport error."""

    def __init__(self, message, *, error_code=None):
        super().__init__(message)
        self.error_code = error_code
