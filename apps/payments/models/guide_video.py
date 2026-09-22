from django.core.validators import FileExtensionValidator
from django.db import models

from apps.shared.models.base import SingletonModel
from core_gisoo_backend.storage_backends.locations import (
    payment_guide_poster_path,
    payment_guide_video_path,
)


class PaymentGuideVideo(SingletonModel):
    """
    Tutorial video shown on the card-to-card payment page
    (sheet: «آموزش پرداخت آسان»).
    """

    title = models.CharField(
        max_length=255,
        default="آموزش پرداخت آسان",
        verbose_name="عنوان نمایشی",
    )

    video = models.FileField(
        upload_to=payment_guide_video_path(),
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=["mp4", "webm", "mov"]),
        ],
        verbose_name="فایل ویدیو",
        help_text="فرمت‌های مجاز: mp4، webm، mov. اگر فایل بگذارید، لینک خارجی استفاده نمی‌شود.",
    )

    external_url = models.URLField(
        max_length=1000,
        blank=True,
        default="",
        verbose_name="لینک خارجی ویدیو",
        help_text="مثال: لینک آپارات، یوتیوب، یا آدرس مستقیم فایل mp4.",
    )

    poster = models.ImageField(
        upload_to=payment_guide_poster_path(),
        blank=True,
        null=True,
        verbose_name="تصویر کاور",
        help_text="اختیاری — تصویر پیش‌نمایش قبل از پخش.",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال در فروشگاه",
        help_text="اگر خاموش باشد، دکمه آموزش ویدیو در صفحه پرداخت ویدیو نشان نمی‌دهد.",
    )

    class Meta:
        verbose_name = "ویدیوی آموزش پرداخت"
        verbose_name_plural = "ویدیوی آموزش پرداخت"

    def __str__(self):
        return self.title or "ویدیوی آموزش پرداخت"

    @property
    def resolved_video_url(self) -> str:
        if self.video:
            try:
                return self.video.url
            except ValueError:
                pass
        return (self.external_url or "").strip()
