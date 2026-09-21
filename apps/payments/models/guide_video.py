from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

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
        verbose_name=_("title"),
    )

    video = models.FileField(
        upload_to=payment_guide_video_path(),
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=["mp4", "webm", "mov"]),
        ],
        verbose_name=_("video file"),
        help_text=_("Upload an mp4/webm/mov file, or leave empty and use external URL."),
    )

    external_url = models.URLField(
        max_length=1000,
        blank=True,
        default="",
        verbose_name=_("external video url"),
        help_text=_("Optional. Used when no uploaded file is set (e.g. CDN / direct mp4 link)."),
    )

    poster = models.ImageField(
        upload_to=payment_guide_poster_path(),
        blank=True,
        null=True,
        verbose_name=_("poster image"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("is active"),
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
