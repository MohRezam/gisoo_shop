import uuid
from datetime import datetime

from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.http import require_POST

MAX_BYTES = 4 * 1024 * 1024


def _image_ext(raw: bytes) -> str | None:
    if raw.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if raw.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if raw.startswith(b"GIF87a") or raw.startswith(b"GIF89a"):
        return "gif"
    if raw.startswith(b"RIFF") and raw[8:12] == b"WEBP":
        return "webp"
    return None


@staff_member_required
@require_POST
def upload_richtext_image(request):
    upload = request.FILES.get("file")
    if upload is None:
        return JsonResponse({"error": "فایلی انتخاب نشده است."}, status=400)
    if upload.size > MAX_BYTES:
        return JsonResponse({"error": "حجم تصویر بیشتر از ۴ مگابایت است."}, status=400)

    raw = upload.read()
    ext = _image_ext(raw)
    if ext is None:
        return JsonResponse(
            {"error": "فقط تصویر JPG، PNG، WEBP یا GIF مجاز است."},
            status=400,
        )

    now = datetime.now()
    name = f"editor/{now:%Y/%m}/{uuid.uuid4().hex}.{ext}"
    saved = default_storage.save(name, ContentFile(raw))
    return JsonResponse({"url": default_storage.url(saved)})
