from corsheaders.defaults import default_headers, default_methods

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:3000",
    "http://194.5.195.195:8080",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = list(default_headers) + [
    "x-client",
    "x-token-id",
    "x-token",
    "X-Token",
    "accept-language",
]

CORS_ALLOW_METHODS = list(default_methods)
