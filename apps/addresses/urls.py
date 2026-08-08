from rest_framework.routers import DefaultRouter

from apps.addresses.apis import (
    AddressViewSet,
)

app_name = "apps.addresses"

router = DefaultRouter()

router.register(
    "",
    AddressViewSet,
    basename="addresses",
)

urlpatterns = router.urls
