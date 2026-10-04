import secrets

from apps.notifications.constants import NotificationStatus
from apps.notifications.services.notification import NotificationService


def generate_six_digit_otp() -> str:
    return str(secrets.randbelow(900000) + 100000)


def send_otp_sms(*, phone_number: str, user=None) -> tuple[str | None, bool]:
    """
    Generate a random OTP and deliver it via the SMS panel.
    Returns (otp, ok). On failure otp is None.
    """
    otp = generate_six_digit_otp()
    notification = NotificationService.send_otp(
        user=user,
        recipient=phone_number,
        otp=otp,
    )
    if notification.status != NotificationStatus.SENT:
        return None, False
    return otp, True
