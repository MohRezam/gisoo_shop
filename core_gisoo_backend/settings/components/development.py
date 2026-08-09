from core_gisoo_backend.settings.components.applications import INSTALLED_APPS
from core_gisoo_backend.settings.components.middleware import MIDDLEWARE

INSTALLED_APPS = [
    app
    for app in INSTALLED_APPS
    if app not in {
        "silk",
        "debug_toolbar",
    }
]

MIDDLEWARE = [
    middleware
    for middleware in MIDDLEWARE
    if middleware not in {
        "silk.middleware.SilkyMiddleware",
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    }
]
DEBUG = False