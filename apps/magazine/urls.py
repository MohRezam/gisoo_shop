from rest_framework.routers import DefaultRouter

from apps.magazine.apis import MagazineViewSet

app_name = "apps.magazine"
router = DefaultRouter()

router.register(
    "magazines",
    MagazineViewSet,
    basename="magazine",
)

urlpatterns = router.urls
