from django.core.management.base import BaseCommand, CommandError

from apps.sms.patterns import PATTERNS
from apps.sms.service import send_pattern_sms


class Command(BaseCommand):
    help = (
        "ارسال آزمایشی پیامک پترن (ملی‌پیامک SendByBaseNumber). "
        "مثال: manage.py send_test_sms --pattern otp_login "
        "--phone 0912xxxxxxx --code 123456"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--pattern",
            default="otp_login",
            help=f"کلید پترن ({', '.join(sorted(PATTERNS))})",
        )
        parser.add_argument(
            "--phone",
            required=True,
            help="شماره موبایل گیرنده",
        )
        parser.add_argument(
            "--code",
            default="",
            help="کد OTP (برای otp_login)",
        )
        parser.add_argument(
            "--order-id",
            default="",
            dest="order_id",
        )
        parser.add_argument(
            "--amount",
            default="",
        )
        parser.add_argument(
            "--minutes-left",
            default="",
            dest="minutes_left",
        )
        parser.add_argument(
            "--consultation-id",
            default="",
            dest="consultation_id",
        )
        parser.add_argument(
            "--product-id",
            default="",
            dest="product_id",
        )

    def handle(self, *args, **options):
        pattern = options["pattern"]
        if pattern not in PATTERNS:
            raise CommandError(
                f"پترن ناشناخته: {pattern}. "
                f"مجاز: {', '.join(sorted(PATTERNS))}"
            )

        data = {
            "code": options["code"],
            "order_id": options["order_id"],
            "amount": options["amount"],
            "minutes_left": options["minutes_left"],
            "consultation_id": options["consultation_id"],
            "product_id": options["product_id"],
        }
        # Drop empty keys so build_vars can report missing ones clearly.
        data = {k: v for k, v in data.items() if str(v).strip()}

        result = send_pattern_sms(
            pattern,
            options["phone"],
            data,
        )

        if result.get("success"):
            self.stdout.write(
                self.style.SUCCESS(
                    f"OK messageId={result.get('message_id')} "
                    f"phone={result.get('phone')}"
                )
            )
            return

        # Avoid Windows console UnicodeEncodeError on Persian text.
        err = result.get("error_message") or ""
        try:
            err.encode(self.stdout.encoding or "utf-8")
        except UnicodeEncodeError:
            err = err.encode("ascii", "replace").decode("ascii")

        self.stdout.write(
            self.style.WARNING(
                "SMS soft-fail (no crash):\n"
                f"  phone={result.get('phone')}\n"
                f"  error={err}\n"
                f"  code={result.get('error_code')}\n"
                f"  provider={result.get('provider_response')}"
            )
        )
