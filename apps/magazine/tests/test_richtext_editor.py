import json

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase

from apps.magazine.models import Magazine
from apps.products.models import Product
from apps.shared.richtext_upload import upload_richtext_image
from apps.shared.widgets import GisooRichTextWidget

User = get_user_model()

PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
    b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
    b"\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


class RichTextEditorTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            phone_number="09127770001",
            is_staff=True,
        )
        self.customer = User.objects.create_user(phone_number="09127770002")

    def test_magazine_and_product_use_the_editor(self):
        request = RequestFactory().get("/admin/")
        request.user = self.staff
        magazine_field = admin.site._registry[Magazine].formfield_for_dbfield(
            Magazine._meta.get_field("content"),
            request,
        )
        product_field = admin.site._registry[Product].formfield_for_dbfield(
            Product._meta.get_field("description"),
            request,
        )
        self.assertIsInstance(magazine_field.widget, GisooRichTextWidget)
        self.assertIsInstance(product_field.widget, GisooRichTextWidget)
        self.assertEqual(magazine_field.widget.attrs["data-gisoo-editor"], "1")

    def _post(self, user, upload):
        request = RequestFactory().post("/admin/richtext-image/", {"file": upload})
        request.user = user
        return upload_richtext_image(request)

    def test_staff_can_upload_an_image(self):
        response = self._post(
            self.staff,
            SimpleUploadedFile("note.png", PNG, content_type="image/png"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)["url"])

    def test_customer_cannot_upload(self):
        response = self._post(
            self.customer,
            SimpleUploadedFile("note.png", PNG, content_type="image/png"),
        )
        self.assertEqual(response.status_code, 302)

    def test_non_image_is_rejected(self):
        response = self._post(
            self.staff,
            SimpleUploadedFile("note.txt", b"hello", content_type="text/plain"),
        )
        self.assertEqual(response.status_code, 400)
