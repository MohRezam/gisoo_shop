from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone

from apps.magazine.apis.magazine import _magazine_cache_ttl
from apps.magazine.models import Magazine, MagazineCategory

PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
    b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
    b"\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


class MagazinePublishWindowTests(TestCase):
    def setUp(self):
        self.category = MagazineCategory.objects.create(name="مراقبت", slug="care")

    def make(self, slug, *, published, when):
        return Magazine.objects.create(
            category=self.category,
            title=slug,
            slug=slug,
            short_description="خلاصه",
            content="<p>متن</p>",
            thumbnail=SimpleUploadedFile(f"{slug}.png", PNG, content_type="image/png"),
            published_at=when,
            is_published=published,
        )

    def test_future_article_stays_hidden_until_its_time(self):
        now = timezone.now()
        live = self.make("live-now", published=True, when=now - timedelta(minutes=5))
        scheduled = self.make("in-two-minutes", published=True, when=now + timedelta(minutes=2))
        draft = self.make("draft", published=False, when=now - timedelta(days=1))

        visible = set(Magazine.objects.live().values_list("slug", flat=True))
        self.assertIn(live.slug, visible)
        self.assertNotIn(scheduled.slug, visible)
        self.assertNotIn(draft.slug, visible)

    def test_cache_expires_when_the_next_article_is_due(self):
        self.make(
            "soon",
            published=True,
            when=timezone.now() + timedelta(seconds=120),
        )
        ttl = _magazine_cache_ttl(600)
        self.assertGreater(ttl, 60)
        self.assertLessEqual(ttl, 120)
