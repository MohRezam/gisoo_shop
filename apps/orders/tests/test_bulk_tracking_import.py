from io import BytesIO

from django.contrib.auth import get_user_model
from django.test import TestCase
from openpyxl import Workbook
from rest_framework.exceptions import ValidationError

from apps.orders.models import Order, OrderStatus
from apps.orders.services.bulk_tracking_import import (
    HEADERS,
    build_empty_tracking_template,
    build_preparing_orders_workbook,
    import_tracking_from_workbook,
    validate_tracking_code,
)
from apps.shipping.models import ShippingMethod

User = get_user_model()


def _workbook_bytes(rows):
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(list(HEADERS))
    for row in rows:
        sheet.append(row)
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return buffer


class BulkTrackingImportTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            phone_number="09121111111",
            first_name="ادمین",
            last_name="سیستم",
        )
        self.user = User.objects.create_user(
            phone_number="09120000001",
            first_name="علی",
            last_name="محمدی",
        )
        self.shipping = ShippingMethod.objects.create(
            title="Post",
            price=50000,
            free_shipping_minimum=0,
            estimated_days=3,
            is_active=True,
        )
        self.order = Order.objects.create(
            user=self.user,
            public_number="ORD-1001",
            phone_number=self.user.phone_number,
            status=OrderStatus.PREPARING,
            province="Tehran",
            city="Tehran",
            postal_code="1234567890",
            address="Test",
            shipping_method=self.shipping,
            products_price=100000,
            shipping_price=50000,
            total_price=150000,
        )

    def test_valid_row_sets_tracking_and_ships(self):
        file_obj = _workbook_bytes(
            [
                ["ORD-1001", "علی", "محمدی", "1234567890", "09120000001"],
            ]
        )

        result = import_tracking_from_workbook(
            file_obj=file_obj,
            changed_by=self.admin,
        )

        self.order.refresh_from_db()
        self.assertEqual(result.success_count, 1)
        self.assertEqual(result.errors, [])
        self.assertEqual(self.order.tracking_code, "1234567890")
        self.assertEqual(self.order.status, OrderStatus.SHIPPED)
        self.assertEqual(self.order.carrier, "post")
        self.assertIsNotNone(self.order.shipped_at)

    def test_letters_in_tracking_code_rejected(self):
        file_obj = _workbook_bytes(
            [
                ["ORD-1001", "علی", "محمدی", "TRK-999", ""],
            ]
        )

        result = import_tracking_from_workbook(
            file_obj=file_obj,
            changed_by=self.admin,
        )

        self.order.refresh_from_db()
        self.assertEqual(result.success_count, 0)
        self.assertEqual(len(result.errors), 1)
        self.assertIn("حرف", result.errors[0].message)
        self.assertEqual(self.order.status, OrderStatus.PREPARING)
        self.assertEqual(self.order.tracking_code, "")

    def test_persian_digits_accepted(self):
        code = validate_tracking_code("۱۲۳۴۵۶۷۸۹۰")
        self.assertEqual(code, "1234567890")

    def test_short_tracking_code_rejected(self):
        with self.assertRaises(ValidationError):
            validate_tracking_code("123")

    def test_wrong_name_does_not_change_order(self):
        file_obj = _workbook_bytes(
            [
                ["ORD-1001", "حسن", "رضایی", "1234567890", ""],
            ]
        )

        result = import_tracking_from_workbook(
            file_obj=file_obj,
            changed_by=self.admin,
        )

        self.order.refresh_from_db()
        self.assertEqual(result.success_count, 0)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(self.order.status, OrderStatus.PREPARING)
        self.assertEqual(self.order.tracking_code, "")

    def test_missing_order_reports_error(self):
        file_obj = _workbook_bytes(
            [
                ["ORD-MISSING", "علی", "محمدی", "1234567890", ""],
            ]
        )

        result = import_tracking_from_workbook(
            file_obj=file_obj,
            changed_by=self.admin,
        )

        self.assertEqual(result.success_count, 0)
        self.assertEqual(len(result.errors), 1)
        self.assertIn("پیدا نشد", result.errors[0].message)

    def test_non_preparing_status_fails(self):
        self.order.status = OrderStatus.WAITING_PAYMENT
        self.order.save(update_fields=["status"])

        file_obj = _workbook_bytes(
            [
                ["ORD-1001", "علی", "محمدی", "1234567890", ""],
            ]
        )

        result = import_tracking_from_workbook(
            file_obj=file_obj,
            changed_by=self.admin,
        )

        self.order.refresh_from_db()
        self.assertEqual(result.success_count, 0)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(self.order.status, OrderStatus.WAITING_PAYMENT)
        self.assertEqual(self.order.tracking_code, "")

    def test_already_shipped_updates_tracking_only(self):
        self.order.status = OrderStatus.SHIPPED
        self.order.tracking_code = "111111"
        self.order.save(update_fields=["status", "tracking_code"])

        file_obj = _workbook_bytes(
            [
                ["ORD-1001", "علی", "محمدی", "999888777666", ""],
            ]
        )

        result = import_tracking_from_workbook(
            file_obj=file_obj,
            changed_by=self.admin,
        )

        self.order.refresh_from_db()
        self.assertEqual(result.success_count, 1)
        self.assertEqual(result.errors, [])
        self.assertEqual(self.order.tracking_code, "999888777666")
        self.assertEqual(self.order.status, OrderStatus.SHIPPED)

    def test_mixed_rows_partial_success(self):
        other_user = User.objects.create_user(
            phone_number="09120000002",
            first_name="سارا",
            last_name="احمدی",
        )
        other = Order.objects.create(
            user=other_user,
            public_number="ORD-1002",
            phone_number=other_user.phone_number,
            status=OrderStatus.PREPARING,
            province="Tehran",
            city="Tehran",
            postal_code="1234567890",
            address="Test 2",
            shipping_method=self.shipping,
            products_price=200000,
            shipping_price=50000,
            total_price=250000,
        )

        file_obj = _workbook_bytes(
            [
                ["ORD-1001", "علی", "محمدی", "111222333444", ""],
                ["ORD-1002", "نام", "غلط", "555666777888", ""],
                ["ORD-MISSING", "سارا", "احمدی", "999000111222", ""],
            ]
        )

        result = import_tracking_from_workbook(
            file_obj=file_obj,
            changed_by=self.admin,
        )

        self.order.refresh_from_db()
        other.refresh_from_db()

        self.assertEqual(result.success_count, 1)
        self.assertEqual(len(result.errors), 2)
        self.assertEqual(self.order.status, OrderStatus.SHIPPED)
        self.assertEqual(self.order.tracking_code, "111222333444")
        self.assertEqual(other.status, OrderStatus.PREPARING)
        self.assertEqual(other.tracking_code, "")

    def test_lookup_by_numeric_id(self):
        self.order.public_number = None
        self.order.save(update_fields=["public_number"])

        file_obj = _workbook_bytes(
            [
                [str(self.order.pk), "علی", "محمدی", "444555666777", ""],
            ]
        )

        result = import_tracking_from_workbook(
            file_obj=file_obj,
            changed_by=self.admin,
        )

        self.order.refresh_from_db()
        self.assertEqual(result.success_count, 1)
        self.assertEqual(self.order.tracking_code, "444555666777")
        self.assertEqual(self.order.status, OrderStatus.SHIPPED)

    def test_template_builders(self):
        empty = build_empty_tracking_template()
        preparing = build_preparing_orders_workbook()
        self.assertTrue(empty.startswith(b"PK"))
        self.assertTrue(preparing.startswith(b"PK"))
        self.assertGreater(len(empty), 100)
        self.assertGreater(len(preparing), 100)
