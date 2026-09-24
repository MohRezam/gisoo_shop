from django.test import SimpleTestCase, override_settings

from apps.sms.client import (
    interpret_send_result,
    normalize_iran_mobile,
    parse_soap_result,
)
from apps.sms.patterns import get_pattern
from apps.sms.service import send_pattern_sms


class NormalizePhoneTests(SimpleTestCase):
    def test_plus_98(self):
        self.assertEqual(
            normalize_iran_mobile("+989121234567"),
            "09121234567",
        )

    def test_98_prefix(self):
        self.assertEqual(
            normalize_iran_mobile("989121234567"),
            "09121234567",
        )

    def test_ten_digit(self):
        self.assertEqual(
            normalize_iran_mobile("9121234567"),
            "09121234567",
        )

    def test_already_normalized(self):
        self.assertEqual(
            normalize_iran_mobile("09121234567"),
            "09121234567",
        )


class ParseResponseTests(SimpleTestCase):
    def test_parse_send_by_base_number_xml(self):
        self.assertEqual(
            parse_soap_result(
                "<SendByBaseNumberResult>9876543210</SendByBaseNumberResult>"
            ),
            "9876543210",
        )
        self.assertEqual(
            parse_soap_result("<string>3811122233</string>"),
            "3811122233",
        )

    def test_interpret_success(self):
        outcome = interpret_send_result("3812345678")
        self.assertTrue(outcome["success"])
        self.assertEqual(outcome["message_id"], "3812345678")

    def test_interpret_error_code_5(self):
        outcome = interpret_send_result("-5")
        self.assertFalse(outcome["success"])
        self.assertEqual(outcome["error_code"], 5)
        self.assertIn("متغیر", outcome["error_message"])


class PatternBuildVarsTests(SimpleTestCase):
    def test_otp_vars(self):
        pattern = get_pattern("otp_login")
        self.assertEqual(
            pattern.build_vars({"code": " 7818 "}),
            ["7818"],
        )

    def test_order_created_vars_order(self):
        pattern = get_pattern("order_created")
        self.assertEqual(
            pattern.build_vars(
                {"order_id": "42", "amount": "150000"}
            ),
            ["42", "150000"],
        )


@override_settings(
    SMS_USERNAME="",
    SMS_PASSWORD="",
    SMS_OTP_BODY_ID=0,
    SMS_ENABLED=False,
)
class SoftFailWithoutCredentialsTests(SimpleTestCase):
    def test_send_pattern_soft_fail(self):
        result = send_pattern_sms(
            "otp_login",
            "09121234567",
            {"code": "123456"},
        )
        self.assertFalse(result["success"])
        self.assertIsNone(result["message_id"])
        self.assertTrue(result["error_message"])
