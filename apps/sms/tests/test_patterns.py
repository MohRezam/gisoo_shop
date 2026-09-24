from django.test import SimpleTestCase, override_settings

from apps.sms.exceptions import SmsPatternError
from apps.sms.patterns import PATTERNS, get_pattern
from apps.sms.service import send_otp


class PatternsRegistryTests(SimpleTestCase):
    def test_otp_panel_text_contains_placeholders(self):
        pattern = get_pattern("otp_login")
        self.assertIn("{0}", pattern.panel_text)
        self.assertIn("لغو11", pattern.panel_text)
        self.assertEqual(pattern.env_attr, "SMS_OTP_BODY_ID")

    def test_unknown_pattern(self):
        with self.assertRaises(SmsPatternError):
            get_pattern("does_not_exist")

    def test_all_patterns_have_unique_keys(self):
        self.assertEqual(
            len(PATTERNS),
            len({p.key for p in PATTERNS.values()}),
        )


@override_settings(
    SMS_USERNAME="",
    SMS_PASSWORD="",
    SMS_OTP_BODY_ID=0,
    DEBUG=True,
    SMS_ENABLED=False,
)
class SendOtpSoftFailTests(SimpleTestCase):
    def test_send_otp_without_credentials(self):
        result = send_otp("9121234567", "445566")
        self.assertFalse(result["success"])
        self.assertEqual(result["phone"], "09121234567")
